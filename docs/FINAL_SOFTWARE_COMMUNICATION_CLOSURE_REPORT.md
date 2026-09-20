# Final Software and Communication Closure Report

Date: 2026-09-20
Scope: software-only closure; no COM, USB, I²C, camera, motor, encoder or
E-stop hardware was opened or probed.

## Objective and baseline

The prior frozen baseline already had one Protocol V1 implementation, bounded
COBS/CRC-32C/CBOR framing, identity-gated serial selection, a fixed-buffer
firmware service, simulator endpoint, replay and Phase-1 zero-output command
path. The remaining genuine gaps were real LD2450 target-report decoding and
a hardware-neutral encoder counter contract. The initial real-radar runtime
also incorrectly continued to feed the radar simulator.

## Changes

| Area | Closure result | Maturity |
|---|---|---|
| LD2450 decoder | Bounded 30-byte target-report parser: header/footer, three slots, documented sign/magnitude X/Y and speed conversion, resolution, noise recovery and 6 m envelope rejection. | SOFTWARE VERIFIED |
| Radar integration | Decoded reports queue into the existing pipeline only in configured `real_radar`; non-simulation mode never injects `RadarSimulator`. Raw evidence is retained. | SOFTWARE VERIFIED |
| Source semantics | `SIMULATION`, `REAL`, `NOT_CONNECTED`, `FAULT` and `DISABLED_PHASE_1` are separated. Firmware ACK/NACK uses `REAL`; Python endpoint stays `SIMULATION`. | SOFTWARE VERIFIED |
| ESP32 transport/protocol | Existing identity-gated duplex transport, COBS/CRC/CBOR, expiry, sequence, ACK/NACK/STATUS, heartbeat and reconnect boundaries were retained. ACK/NACK shared vectors were regenerated. | SOFTWARE VERIFIED |
| Encoder contract | Explicit timestamped count, optional verified modulus/wrap, optional jump limit, stale/no-data/invalid/fault states. No voltage, polarity, pulses/revolution, speed or ground-distance assumption. | SOFTWARE VERIFIED |

The LD2450 target report uses the published `AA FF 03 00` header, three
eight-byte records and `55 CC` footer. It does not implement undocumented
configuration commands or other frame types. Radar X/Y remains a local frame;
it is never transformed into GNSS coordinates.

## Test evidence

| Check | Result |
|---|---|
| Focused LD2450/runtime/encoder tests | 21 passed |
| Full backend suite | 97 passed, 2 dependency deprecation warnings |
| Frontend suite | 25 passed |
| TypeScript | passed |
| Vite production build | passed; existing lazy MapView chunk advisory only |
| Python Protocol V1 vectors/transport tests | 10 passed |
| Firmware strict compilation | passed with `-std=c11 -Wall -Wextra -Werror -fsyntax-only` |
| Fresh firmware host executable compilation | passed |
| Firmware Protocol V1 host executable | passed (`tark_host_protocol_tests_17944.exe`, exit 0) |
| Firmware service host executable | passed (`tark_host_service_tests_17944.exe`, exit 0) |

Deterministic coverage includes parsed/simulated radar through perception,
tracking, TTC/PV-SOE, bounded zero command, Protocol V1 simulator ACK/NACK,
recording and replay. Existing tests cover malformed CRC, expiry, duplicate
sequence, configuration mismatch, heartbeat, transport recovery, WebSocket
observation-only publication and the absence of motor/traction HTTP routes.

## Safety checks

- `traction == DISABLED_PHASE_1`; left and right applied values remain zero.
- Browser, public demo, GNSS, map and sensor adapters have no motor authority.
- No simulated radar or ESP32 response is labelled real.
- The physical E-stop/K1 path remains independent and is not software
  substituted.

## Hardware-only verification remaining

LD2450 physical identity/serial output/calibration; ESP32 board identity,
firmware flash and USB exchange; encoder electrical interface/counts; MDD10A,
motor, contactor and E-stop behavior; sensor calibration; and vehicle-level
validation all require controlled physical evidence.

## Freeze decision

No further software or software-communication implementation gap was found.
Both freshly compiled firmware host executables ran successfully with exit code
0. The software and communication stack is ready to freeze. This is not
physical validation, mine certification, traction authorization or a claim
that hardware works.
