# R3 observation extension of the existing TARK protocol

Status: IMPLEMENTED / FIXTURE-VERIFIED where reported in the test record;
HARDWARE-UNVERIFIED. No new framing implementation. No board-specific USB,
entropy, interrupt, encoder-counter or watchdog implementation is inferred.

## Envelope and messages

The authoritative codec remains `communication/esp32/protocol.py` and
`firmware/esp32/main/protocol`. Envelope VERSION stays **2**; retired VERSION 1
remains rejected. Big-endian header `!HBBIQQ`: magic 0x544B, version, type,
payload length, sequence, timestamp. Canonical flat CBOR; payload ≤512 bytes;
CRC-32C; bounded COBS; zero delimiters; complete frame ≤640 bytes.

| Type | Meaning | Authority |
|---|---|---|
| 1 COMMAND | Existing disabled legacy research command | R3 never submits it |
| 2 ACK | Exact pending command/heartbeat correlation | Not physical actuation |
| 3 NACK | Existing rejection contract | No authority |
| 4 HEARTBEAT | Existing session liveness | Cannot extend command expiry |
| 5 STATUS | Existing supervisor telemetry | Does not acknowledge a command |
| 6 SESSION_OPEN | Pi challenge + configuration ID | No command |
| 7 SESSION_READY | Echo challenge + MCU boot/generation session | No identity proof by itself |
| 8 OBSERVATION | New `ENCODER_V1` payload below | Measurement only |

The extension is explicitly named ENCODER_V1, not a silent replacement of a
command payload. Older VERSION-2 clients without type 8 reject it; deploy
matched host/firmware versions. No downgrade or unknown-message acceptance.

## ENCODER_V1 payload

Exactly sixteen keys, canonical CBOR ordering:

| Field | Representation |
|---|---|
| kind | `ENCODER_V1` |
| node_id / source_id | Printable ASCII, 1–16 / 1–32 bytes |
| session_id | Existing 48 lower-case hexadecimal boot/generation token |
| configuration_hash | Printable ID/hash ≤64 bytes, must match active session |
| calibration_id | Printable versioned calibration ID ≤64 bytes or null |
| source_mode | Firmware encodes REAL; explicit software simulator uses SIMULATION |
| left_count / right_count | Signed 32-bit counts, not speed |
| source_counter / drop_count / fault_bits / invalid_edges | Unsigned 32-bit |
| lost_edges | Unsigned 32-bit or null when not measurable |
| interval_start_ns / interval_end_ns | MCU monotonic interval; start < end ≤ envelope timestamp |

Envelope sequence is unsigned 32-bit. Observation sequence and monotonic time
have their own host-side progression checks. Negative counts encode canonical
CBOR major type 1. Missing/extra fields, booleans in numeric fields, bad CRC,
noncanonical CBOR, out-of-range values, session/config mismatch, replay-mode
packets, duplicates and old observation timestamps are rejected.

## State transitions and failure semantics

```text
UNAVAILABLE --reviewed platform binding--> NO_SESSION
NO_SESSION --SESSION_OPEN / challenge response--> SESSION_ACTIVE
SESSION_ACTIVE --valid type 8--> retained measurement (not command ACK)
SESSION_ACTIVE --disconnect/reboot--> NO_SESSION (old session rejected)
malformed frame --> reject / recover at next delimiter
stale observation --> unqualified evidence; never keep refreshing on duplicates
```

`open_observation_session` sends only type 6. `receive` type 8 never changes
`last_exchange_ns`, command pending state, accepted output or motion authority.
The channel separately needs a valid MCU→Pi time mapping; host arrival is not
renamed capture time. A new MCU boot invalidates the old mapping.

`tark_protocol_service_encoder` binds the service's active session/configuration
to a provided measurement and uses the existing encoder/CRC/COBS path. The
measurement collector owns monotonically advancing sequence/counters and must
restart its observation session before sequence exhaustion. It does not call
motor or supervisor-accept APIs. Firmware remains `DISABLED_PHASE_1`.

The existing legacy command watchdog/expiry logic is unchanged. Physical
watchdog, USB enumeration and actual measurement interrupts remain unverified.

## Shared fixtures and exact host test

`r3_protocol_vectors.json` is consumed by Python and generates
`firmware/esp32/tests/r3_protocol_vectors.h` using the existing generator:

```text
python scripts/generate_protocol_vectors.py --r3 --refresh
python -m pytest backend/tests/test_r3_protocol.py -q
```

The C host executable builds the production observation responses, byte-compares
them with the shared vectors, decodes/validates canonical CBOR, and prints frames
that Python decodes through the production session client. Signed counts,
extremes, null calibration/lost-edge values and malformed inputs are included.

Execution history is retained in `R3_VERIFICATION_REPORT.md`. The earlier
31 blocked legacy cases are not retroactively called passing: a later normal
host run actually executed them successfully. The latest full run passed 419
tests but Windows blocked the newly compiled `r3_observation_host.exe` with
WinError 4551. Its earlier successful run is evidence for that earlier build,
not a replacement for the latest blocked gate. No security-policy changes or
alternate execution route were used. No result verifies physical hardware.
