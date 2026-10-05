# ESP32, Encoder and MDD10A Integration Boundary

## Status

This is a software-ready, hardware-unverified research-prototype boundary.
The present firmware state is `DISABLED_PHASE_1`; every firmware motor request
is clamped to `[-1, 1]` and its applied left/right outputs remain `0.0`.
Neither an ACK, a successful USB open, nor a simulator result is evidence that
a contactor, MDD10A, motor, encoder, or E-stop has operated physically.

## Sole control path

`radar/sensor health → TARK pipeline → PV-SOE decision → BoundedCommand →
Pi ESP32Client → framed USB transport → ESP32 protocol validation → command
supervisor → disabled motor-driver boundary`

The browser has no command endpoint, and GNSS, map, routing, camera, thermal,
IMU and diagnostics are observers only. The independent physical NC E-stop and
K1 contactor path are not software-replaced. GPIO13 is reserved for auxiliary
diagnostic status only, not as the primary safety path.

## Immutable reviewed mapping

| ESP32 J1 | GPIO | MDD10A logic connection |
|---|---:|---|
| J1-15 | GPIO9 | P4 PWM1 |
| J1-16 | GPIO10 | P5 DIR1 |
| J1-17 | GPIO11 | P2 PWM2 |
| J1-18 | GPIO12 | P3 DIR2 |
| J1-21 | 5V | logic supply as shown in engineering schematic |
| J1-22 | GND | P1 GND |

MDD10A terminals remain T1 M1B left motor, T2 M1A left motor, T3 POWER+ from
the K1 main contact, T4 POWER− to N-TRACTION−, T5 M2A right motor, and T6 M2B
right motor. This document does not authorize wiring, energizing, or changing
those connections.

Encoders remain left A J1-4/GPIO4, left B J1-5/GPIO5, right A J1-6/GPIO6 and
right B J1-7/GPIO7. Encoder VCC and output-interface details are `TBD / VERIFY`.
Their data is called **wheel response**, never ground-truth vehicle speed.

## Protocol controls

[Protocol V2](ESP32_PROTOCOL_V2.md) is COBS framed and protected by CRC-32C,
with explicit sessions and receiver-local bounded expiry. The Pi client rejects an
expired command, non-monotonic sequence, sequence outside uint32 range,
non-finite values, a negative permitted speed, and wheel command magnitudes
greater than one before it writes a frame. The simulator additionally exercises
configuration-hash mismatch and replay rejection. Its response includes
`DISABLED_PHASE_1` and zero applied outputs by design.

`IdentityGatedESP32UsbTransport` discovers ports without treating them as an
ESP32. A selected device path, a reviewed baudrate, and operator-recorded
identity evidence are all required before it can open. This is a preparation
mechanism, not an automatic hardware-enable mechanism.

## Hardware-arrival order

1. Identify the exact ESP32-S3 board and record its port, manufacturer,
   product, serial/VID/PID evidence. Do not infer identity from the COM port.
2. Set the reviewed USB path and baudrate in local configuration; use the
   identity-gated transport only after recorded evidence.
3. Complete a reviewed board RX/TX, unique-boot-identity, scheduler/disconnect
   and watchdog binding first; current app_main remains unavailable. Then,
   under a separately approved procedure, flash and inspect firmware identity,
   Protocol V2, configuration hash,
   sequence/expiry/NACK behavior and status reporting with traction isolated.
4. Verify the independent physical E-stop/contactor path separately. GPIO13
   may only be checked as a diagnostic indication.
5. Verify encoder supply/output interface against the exact JGB37-520 variant
   before enabling capture. Check pulse direction, missing signal, stale data,
   and left/right mismatch while terminology remains wheel response.
6. Verify the exact MDD10A variant and wiring against the locked schematic.
   Keep traction physically isolated until the documented Phase-2 review and
   controlled safety test are approved.

## Explicitly not verified

ESP32 USB enumeration, board flash, ESP-IDF build/flash, USB baudrate,
watchdog registration, MDD10A electrical output, motor direction/motion,
encoder voltage/interface/counts, K1 behaviour, physical E-stop, and any
traction operation all require hardware and are not claimed here.
