# V9 GNSS Integration — LC29H(AA)

## Scope and safety isolation

The target receiver is the **Waveshare LC29H(AA)** on USB with its supplied active antenna. This software is designed and implemented for development; it is not physically verified, validated for accuracy, RTK fixed, or connected to motion authority. GNSS, map, route, address and browser location never reach the ESP32 command, motor driver, PV-SOE decision, verification path or E-stop.

## States and contract

`NO_RECEIVER`, `SEARCHING`, `NO_FIX`, `2D_FIX`, `3D_FIX`, `STALE`, `ERROR` and `ONLINE` are exposed with a reason. A valid contract carries vehicle ID, monotonic receive timestamp, source (`GNSS`, `SIMULATION`, `REPLAY`, `UNKNOWN`), coordinates, optional altitude/speed/heading/accuracies, fix type, satellites, freshness, quality and status. Browser device location is a separate local browser type and cannot populate this contract.

## Before hardware: implemented test modes

The parser accepts checksum-validated standard NMEA RMC/GGA/GSA sentences and safely rejects malformed input. GSA is used only for its receiver-reported no-fix/2D/3D mode; altitude is never treated as dimensional proof. The service evaluates freshness, coordinates, speed, satellite count, accuracy, timestamp order and position jumps. Breadcrumbs are bounded by `TARK_GNSS_BREADCRUMB_LIMIT`. `GnssSimulator` is deterministic and always labelled `SIMULATION`; replay can feed the same normalized `GnssFix` model. No production path invents a coordinate.

Freshness mutates the service state to `STALE`, hides the current position from the live API, and returns cleanly to `ONLINE` only after a fresh accepted fix. RMC measurement UTC (when date/time are present) is kept separate from monotonic receipt time. GGA altitude is not treated as proof of a 3D fix; its actual quality code is retained instead.

## Real serial architecture

`app.gnss_driver.GnssReader` is a single daemon thread around an optional `pyserial` opener: serial bytes → bounded line framing → checksum decoder → RMC/GGA aggregation → `GnssLocationService`. It handles split/multiple CR/LF lines, corrupt input, oversized lines, close, disconnect and bounded retry. It does not run reads on FastAPI's event loop and will not select an unverified device automatically. `python -m app.gnss_probe --device <verified-path>` is read-only hardware bring-up diagnostics; it prints candidates, reader state/counters, raw timing and normalized location state while traction stays disabled.

## Hardware arrival procedure

1. Keep traction disabled and motor power disconnected.
2. Connect only the LC29H(AA) USB cable and active antenna; identify its USB serial device using OS device-management tools.
3. Set `TARK_GNSS_DEVICE_PATH` to that confirmed path and set the verified baud/interface settings. Do not accept an arbitrary `/dev/ttyUSB*` candidate.
4. Start with discovery only. Confirm the reported device identity and raw NMEA stream before enabling any normalized GNSS source.
5. Verify checksum-valid RMC/GGA input, no-fix behavior, 2D/3D transitions, timestamps, satellite count, accuracy and stale timeout in a controlled outdoor test.
6. Measure actual accuracy against known reference points. Do not claim centimetre-level or RTK-fixed position.
7. Only then configure the real GNSS adapter; keep map/routing informational and preserve traction-disabled Phase 1.

## Configuration and troubleshooting

Use `.env.example` for device path, baud, freshness, maximum speed/jump, satellite/accuracy minimums and breadcrumb limit. A blank path deliberately reports no receiver. Corrupt lines do not terminate the application. `STALE` hides the current vehicle location rather than showing an old coordinate as live. Address and route provider settings are optional, server-side, throttled by operator workflow, and unavailable by default.

## Physical verification still required

LC29H(AA) USB enumeration, its exact NMEA/vendor output, antenna performance, receiver accuracy, placement, electromagnetic behaviour, real-world stale/dropout handling and all safety validation remain physical verification tasks.
