# V9 Prompt 7B — Firmware Responses and Bidirectional Boundary

> HISTORICAL BASELINE — SUPERSEDED BY LATER RED-TEAM / CORRECTION RELEASE.
> Retained as a dated record, not current completion or protocol authority.
> Use [R1 release index](TARK_RELEASE_INDEX.md),
> [Protocol V2](ESP32_PROTOCOL_V2.md) and
> [supersession register](TARK_SUPERSESSION_REGISTER.md).

## Gap closed

Task 7A froze framing and COMMAND decoding but intentionally deferred
firmware-side response encoding and the byte-stream service. Task 7B adds a
single bounded response frame builder and a hardware-neutral firmware service
that performs the following host-testable chain:

`COMMAND frame → COBS/CRC/envelope → CBOR validation → supervisor → ACK/NACK
frame → injected TX callback`

## Implemented

- `response.*` creates canonical CBOR ACK, NACK and STATUS payloads, adds the
  V1 envelope/CRC-32C/COBS delimiters, and rejects oversize outputs.
- ACK/NACK responses use the frozen fields and always contain
  `DISABLED_PHASE_1`, `applied_left: 0`, and `applied_right: 0`.
- `service.*` has one fixed 640-byte RX accumulator, delimiter recovery,
  partial/multiple-frame support, command/heartbeat handling, an injected
  atomic TX callback, counters, and no dynamic allocation.
- A valid COMMAND is accepted only through the existing supervisor. Duplicate,
  expired and invalid commands remain rejected. Explicit configuration mismatch
  produces `CONFIGURATION_MISMATCH`; malformed payloads produce
  `INVALID_PAYLOAD`.
- Pi-side `ESP32Client` correlation and `BidirectionalSerialTransport` mock
  coverage remain in the existing Protocol V1 implementation; no web endpoint
  was added.

## Interoperability evidence

The firmware Task 7B host source compares C-generated ACK, NACK and STATUS
bytes directly against the JSON-derived shared vectors, then feeds a split
Python COMMAND vector through the C service and compares its emitted ACK to
the same vector. Python decodes the canonical vectors directly and exercises
corruption recovery plus exact response correlation.

The normal `TarkSystem` simulation now sends its locally-generated bounded
command through `ESP32ProtocolSimulator`, receives the correlated feedback,
and publishes it under a `source_mode: SIMULATION` protocol object. The result
remains `DISABLED_PHASE_1` with both applied values zero. This is a controlled
software integration test, not an attempt to open a serial device.

## Regression evidence

The complete backend suite was run twice during this task: once after the
initial service integration and once after correcting the response builder to
write the full 32-bit big-endian payload length. Those historical counts have
since been superseded: the current backend regression suite reports **87
passed**, and the latest frontend regression suite reports **23 passed**.
Protocol V1 framing, CBOR validation and the shared Python/C vectors remain
implemented. The frontend TypeScript check and Vite production build passed in
that task.
Strict GCC syntax compilation of both
firmware host-test sources and all related C modules passed with `-Wall
-Wextra -Werror`.

An authority search excluding generated artifacts found `ESP32Client.submit()`
only in backend tests and the locally owned simulation path; there is no
frontend, browser, map, camera, GNSS, routing, thermal, IMU or dashboard call
path to it. The existing API test continues to assert no direct motor,
traction, or command route exists.

## Limits and maturity

| Item | State |
|---|---|
| Protocol/response source | IMPLEMENTED |
| Python protocol/vector tests | FUNCTIONAL |
| C source strict compilation | FUNCTIONAL BUILD CHECK |
| C host executable | not launched here: local application-control policy blocks newly built executables |
| Physical ESP32/USB | NOT VERIFIED |
| Physical MDD10A, motors, encoders, contactor, E-stop | NOT VERIFIED |

No ESP-IDF build tool was available in this environment. The firmware service
does not bind any physical USB facility; Task 7C/hardware bring-up must bind an
identity-verified board transport and execute the host tests on a permitted
build host before flashing. Phase 1 traction remains permanently disabled.
