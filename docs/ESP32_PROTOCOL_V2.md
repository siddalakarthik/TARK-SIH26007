# TARK Pi ↔ ESP32 — Protocol V2

This is the sole current wire contract for TARK PHASE-1 SOFTWARE EVIDENCE RELEASE R1.
**V1 is superseded and rejected**, not auto-detected or silently reinterpreted. The user explicitly approved the session revision
during Prompt 2. Python, firmware and shared vectors are revised together.
Executable references: `backend/app/communication/esp32/protocol.py`,
`firmware/esp32/main/protocol/`, and `protocol_vectors.json`.

## Authority and compatibility

ACK means software command acceptance, never motor movement, brake/coast,
contactor isolation, physical identity or commissioning. All Phase-1 applied
outputs are zero; `output_state = DISABLED_PHASE_1`. The browser and replay
have no actuation authority. Nonzero vector values are **PROTOCOL
INTEROPERABILITY TEST ONLY — NO ACTUATION AUTHORITY**.

Both peers must run V2. There is no V1 fallback. The protocol is not a
cryptographic authentication channel: CRC detects corruption, while sessions
prevent prior-session replay under the unique-boot-identity requirement below.
Protection against malicious peer impersonation is not claimed.

## Frame

`00 | COBS(body + CRC32C) | 00`

| Offset | Bytes | Field |
|---:|---:|---|
| 0 | 2 | Magic `0x544B`, big-endian |
| 2 | 1 | Version `2` |
| 3 | 1 | Message type |
| 4 | 4 | Unsigned payload length, at most 512 |
| 8 | 8 | Unsigned sequence slot; semantic range 0…`0xFFFFFFFF` |
| 16 | 8 | Unsigned timestamp in nanoseconds |
| 24 | N | Canonical CBOR map |
| 24+N | 4 | Big-endian CRC-32C of header + payload |

Maximum complete frame: 640 bytes. Standard COBS; embedded zero bytes in
encoded runs are invalid. CRC reflected Castagnoli polynomial `0x82F63B78`,
initial and final XOR `0xFFFFFFFF`; `123456789` → `0xE3069283`.
Wrong magic/version/type/length/CRC is rejected before payload interpretation.

## Canonical CBOR profile

One definite-length flat map, at most 24 entries. Keys are unique nonempty
printable ASCII strings (32…126), at most 31 bytes; string values at most 127
bytes. Values may be nonempty printable ASCII text, unsigned or negative
CBOR integers, finite binary16/32/64 floats, booleans or null, subject to the
message schema. Integer encodings must be shortest; floats use the shortest
exact IEEE representation. Keys use canonical encoded-length/byte ordering.
Duplicate keys, trailing objects, indefinite forms, nesting, arrays, tags,
byte strings, NaN, infinity and non-shortest encodings are rejected.

Unsigned fields require integers, not booleans or integral floats. Timestamp
fields are uint64; sequence/heartbeat uint32. Command speed/wheel fields accept
finite floats or integers exactly representable in binary64; permitted speed
is nonnegative and each wheel value is in [-1, 1]. Signed wheel encodings are
serialization tests only. Firmware compilation requires IEEE binary32/binary64.

## Exact payloads

Unknown keys are rejected. Listed fields are mandatory, except COMMAND's
optional `checksum`, which may only be null (integrity is the envelope CRC).

| Type | Value | Payload |
|---|---:|---|
| COMMAND | 1 | `protocol_version`, `sequence`, `timestamp_ns`, `valid_until_ns`, `state`, `permitted_speed_mps`, `left_command`, `right_command`, `heartbeat`, `reason_code`, `configuration_hash`, `session_id` |
| ACK | 2 | `accepted: true`, `reason`, `output_state`, `applied_left: 0`, `applied_right: 0`, `source_mode`, `configuration_hash`, `session_id` |
| NACK | 3 | Same fields as ACK, but `accepted: false` and a rejection reason |
| HEARTBEAT | 4 | `protocol_version`, `configuration_hash`, `session_id` |
| STATUS | 5 | `reason`, `output_state`, `source_mode`, `configuration_hash`, `session_id` |
| SESSION_OPEN | 6 | `request_id`, `configuration_hash` |
| SESSION_READY | 7 | `request_id`, `session_id`, `configuration_hash`, `source_mode` |

COMMAND requires header/payload sequence and timestamp equality, version 2,
current session/configuration, state in NORMAL/WARN/RESTRICT/UNKNOWN/STOP,
nonempty ASCII `reason_code` at most 31 bytes, and valid numeric bounds.

## Independent clocks and bounded lifetime

`ttl_ns = valid_until_ns - timestamp_ns`, **0 < ttl_ns ≤ 500,000,000**.
The 500 ms ceiling comes from the existing Phase-1 timeout configuration;
configuration now also rejects a timeout above this ceiling. At receipt:
`local_expiry_ns = receiver_now_ns + ttl_ns`. Overflow is rejected.
Expiry occurs at `receiver_now_ns >= local_expiry_ns`, even without a new
frame. Pi and ESP32 absolute monotonic epochs are never compared.

The Pi checks its own sender deadline before queueing and during transmission.
Transport delay is not measured by this duration contract; no synchronized
clock or physical latency guarantee is claimed. A heartbeat has its own
correlated response but does not extend or reactivate a command deadline.
Receiver clock rollback forces the logical safe state.

## Session, restart and reconnect

1. Pi sends SESSION_OPEN, sequence 0, fresh random 32-lowercase-hex `request_id`
   and configured hash. Header timestamp is the Pi request time.
2. Receiver requires an injected unique-per-boot 32-lowercase-hex boot identity.
   It increments a uint64 generation for every valid open, resets supervision,
   and constructs `session_id = boot_identity + generation_as_16_hex_digits`.
3. SESSION_READY echoes request, configuration, sequence 0 and Pi timestamp;
   the Pi accepts it only while that request is pending and unexpired.
4. Subsequent messages use this exact 48-hex session. Commands and heartbeats
   have strictly increasing shared sequence numbers; no wrap inside a session.
5. Disconnect flushes queued TX, partial RX and pending correlation and
   retires the session. A new handshake is required. Lost responses also
   retire a timed-out session, allowing recovery from reboot without unplug.

Replayed opens always generate a different session; old commands/responses
cannot acquire the new session. A board adapter MUST supply a fresh boot
identity across reboot and serialize RX/tick/disconnect calls. A static or
reused boot ID is not an acceptable physical binding. `app_main` supplies no
invented identity or USB transport and stays explicitly unavailable. Protocol
tests inject deterministic identities only in the host test process.

## Responses, correlation and health

ACK/NACK header sequence and timestamp echo the command or heartbeat. Pi
requires the exact schema, current session/configuration/source, an outstanding
sequence, matching echoed timestamp, and arrival before its pending deadline.
ACK reason must match the pending message: `COMMAND_ACCEPTED_DISABLED_PHASE_1`
or `HEARTBEAT_ACCEPTED`. Missing fields never default to success. Late,
duplicate, unknown, malformed and wrong-source responses are rejected.

NACK reasons: DUPLICATE_SEQUENCE, OLD_SEQUENCE, OUT_OF_ORDER_SEQUENCE,
COMMAND_EXPIRED, HEARTBEAT_TIMEOUT, CONFIGURATION_MISMATCH, SESSION_MISMATCH,
INVALID_PAYLOAD, INVALID_VERSION, INVALID_CRC, INVALID_LENGTH,
INVALID_LIFETIME, NOT_ENABLED, INTERNAL_FAULT, UNEXPECTED_MESSAGE.
STATUS accepts those reasons plus NONE, uses receiver-local timestamp and
last supervised sequence. Pi requires its last correlated sequence and an
increasing status timestamp. STATUS is telemetry, never ACK or a freshness
renewal. Uncorrelatable corrupt frames may be dropped without response.

Pending commands/heartbeats: maximum 64, oldest superseded at capacity,
deadline at the earlier of sender expiry and host response timeout. Terminal
history is bounded to 256: ACKNOWLEDGED, REJECTED, EXPIRED, SUPERSEDED,
PROTOCOL_ERROR. All client correlation operations use a lock.

Only a recent validated ACK yields ONLINE; correlated NACK yields DEGRADED.
No validated exchange yields NOT_CONNECTED; expired feedback yields STALE
(or NOT_CONNECTED after session retirement). Worker liveness is reported
separately. Handshake completion alone is not ONLINE. Stale accepted feedback
is not retained as the current display result.

Production firmware response source is REAL; in-process simulator source is
SIMULATION. Neither is physical verification. USB identity gating remains
separate and must be satisfied before a real serial opener may be used.

## Service and tests

The C service has a fixed RX buffer and injected TX callback. Independent
`tark_protocol_service_tick()` checks expiry/heartbeat and emits STATUS at
250 ms intervals while a session exists. Safe state does not depend on another
command arriving. There is no GPIO/PWM/USB access in this service. Board RX/TX,
periodic scheduling, boot identity and hardware watchdog binding remain pending.

`protocol_vectors.json` is the shared source of payloads, canonical/raw CBOR,
CRC, frames and expected semantic results. `scripts/generate_protocol_vectors.py`
generates the checked C header; `--refresh` deliberately recomputes vector
bytes after declared changes. Python consumes JSON, C consumes that header.
Fresh C host tests plus the stdin/stdout interoperability harness test Python
command → C validation/supervision → C response → Python correlation. No
physical flashing, USB, watchdog, motors, encoders or E-stop is verified.
