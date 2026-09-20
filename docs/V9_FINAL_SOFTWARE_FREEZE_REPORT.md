# V9 Final Control-Stack Software Freeze

## Determination

**SOFTWARE ARCHITECTURE FROZEN** for the pre-hardware research-prototype
baseline. The authority chain is frozen as:

`PV-SOE → BoundedCommand → ESP32Client → Protocol V1 → identity-gated
transport boundary → firmware service → supervisor → disabled motor boundary`

ACK/NACK/STATUS travel back through Protocol V1 and are correlated to the
exact command sequence on the Pi side. The browser, map, routing, GNSS,
camera, thermal, IMU, fleet views, REST, and WebSocket remain monitoring-only.
The physical NC E-stop/K1 contactor path remains independent.

This freeze does **not** enable traction. The final Phase 1 output condition is
`DISABLED_PHASE_1`, `applied_left = 0`, `applied_right = 0`.

## Final status

| Subsystem | Implemented | Functional evidence | Verified / validated | Physically verified |
|---|---|---|---|---|
| PV-SOE / bounded command | Yes | backend tests | simulation only | No |
| Protocol V1 COBS/CRC/CBOR | Yes | shared Python vectors + strict C compile | byte contract reviewed | No |
| Pi correlation / bounded transport | Yes | mocked serial and protocol tests | simulation/mock only | No |
| USB identity gate | Yes | unit tests; requires evidence before open | software behavior only | No |
| Firmware RX / supervisor / responses | Yes | strict C compilation; vector host source | host executable pending permitted host | No |
| MDD10A boundary | Yes | source and host-test source keeps zero | software-only | No |
| Encoder boundary | Yes | simulation boundary; wheel response only | software-only | No |
| Physical E-stop / contactor | No software substitution | intentionally independent | not applicable | No |

## Final protocol state

`docs/ESP32_PROTOCOL_V1.md` is the sole Protocol V1 definition. The canonical
`protocol_vectors.json` is consumed directly in Python and generates the C
host-test header. It fixes exact CBOR, CRC-32C, COBS, frame bytes, sequence and
timestamp behavior for COMMAND, ACK, NACK, STATUS and HEARTBEAT. Firmware
sources have one response builder and one fixed-buffer byte-stream service;
there is no second control protocol.

## Transport and resource audit

- `IdentityGatedESP32UsbTransport` never chooses a port automatically. It
  requires selected path, reviewed baudrate and operator-recorded identity
  evidence before opening.
- The same verified object now supports read, write and close, so it can be the
  single duplex endpoint used by `BidirectionalSerialTransport`.
- Pi queues, Pi frame accumulator and firmware service buffers are bounded.
  Protocol payload limit is 512 bytes; full frame limit is 640 bytes.
- The serial worker permits one reader, one queued writer, bounded queues,
  clean close and reconnect retry. It is outside FastAPI's event loop.
- Firmware service uses fixed storage and an injected TX callback. It contains
  no dynamic allocation, GPIO, PWM or physical USB binding.

## Safety red-team result

Repository authority search excluded generated build artifacts and found
`ESP32Client.submit()` only in backend tests and `TarkSystem`'s explicitly
labelled in-process simulation. No frontend source calls it. No GPIO/PWM/LEDC
binding exists. MDD10A code clamps requests but always applies zero in Phase 1.
The preserved mappings are:

- left encoder A/B: GPIO4/GPIO5; right encoder A/B: GPIO6/GPIO7;
- MDD10A PWM1/DIR1: GPIO9/GPIO10; PWM2/DIR2: GPIO11/GPIO12;
- encoder data is **wheel response**, never ground-truth vehicle speed;
- GPIO13 remains auxiliary diagnostic only; it is not the physical E-stop.

## Test and build evidence

The full suite was run twice after the final gate integration.

| Check | Final result |
|---|---|
| Python backend suite | 57 passed |
| Frontend unit suite | 17 passed |
| TypeScript build check | passed |
| Vite production build | passed |
| C strict compilation | passed: `-std=c11 -Wall -Wextra -Werror -fsyntax-only` |
| ESP-IDF build | unavailable in this environment; not claimed |
| Firmware host executable | not launched: local application-control policy blocks newly compiled executables |

Pytest emitted only environmental/dependency deprecation warnings and a
non-writable `.pytest_cache` warning. Vite emitted its existing MapView chunk
size advisory; it is a performance follow-up, not a control-stack defect.

## Known remaining work

No additional pre-hardware architecture change is recommended. The remaining
work is physical evidence and controlled bring-up:

1. Keep the prototype unpowered and traction isolated.
2. Identify and photograph the exact ESP32-S3 board; record manufacturer,
   product, VID/PID, serial, revision and responsible operator.
3. Record that evidence in the identity gate; select an explicitly reviewed
   device path and baudrate—never infer identity from a COM/tty name.
4. Run the C host executables on a permitted build host, then run the ESP-IDF
   build for the actual board target. Do not flash yet if either fails.
5. Flash only the reviewed firmware; record firmware version, Protocol V1 and
   configuration hash at boot with traction still isolated.
6. Establish read-only USB traffic; check STATUS and malformed-frame recovery.
7. Exercise COMMAND, ACK, NACK, heartbeat timeout, reconnect and restart while
   verifying the reported output remains `DISABLED_PHASE_1` and zero.
8. Verify exact encoder variant, VCC/interface and GPIO wiring; manually rotate
   wheels and record wheel-response behavior. Do not call it ground speed.
9. Verify the independent NC E-stop/K1 contactor path and GPIO13 diagnostic
   indication separately; diagnostic visibility is not traction proof.
10. Verify the exact MDD10A model/terminal wiring against the locked schematic;
    retain traction isolation until a separately approved physical test phase.

## Final honesty statement

No physical ESP32, USB communication, MDD10A, motor movement, encoder,
hardware watchdog, contactor, E-stop or traction behavior has been verified.
The final software architecture is frozen because the remaining work requires
physical hardware evidence, not another architecture rewrite.
