# V9 Prompt 4 — Sensor Integration Report

## Audit findings and fixes

- **Correct:** Phase 1 remains traction-disabled; browser camera/location boundaries remain separate; map remains observation-only.
- **Implemented / software verified:** BNO055 and MLX90640 have concrete optional-library readers, strict input validation, freshness/error states and identity-gated runtime bootstrap. A worker starts only in the reviewed hardware-capable runtime after a configured address and recorded identity evidence; it does not probe or fabricate samples by default.
- **Bug fixed:** camera frame-read failure could loop indefinitely while retaining a stale capture. It now releases after a configurable threshold, performs bounded reconnects and prevents duplicate workers.
- **Hardware-dependent:** I²C identities, addresses, electrical levels, actual BNO055 modes, MLX90640 performance, camera UVC profile and all calibration remain unverified.

## New/modified implementation

- `app.imu.Bno055Adapter` and `app.thermal.Mlx90640Adapter` expose discovery, state, validation, sequence and freshness. `TarkSystem` now selects their concrete optional-library reader only after configuration and identity gating.
- New `/api/v1/imu` and `/api/v1/thermal` observation endpoints provide status and read-only diagnostics.
- `PiUvcCameraAdapter` now has failure threshold/reconnect state handling.
- Configuration documents camera recovery and IMU/thermal I²C boundaries. Optional dependency groups are `.[camera]`, `.[imu]`, `.[thermal]`.

## Three review passes

1. Functional: mocked valid/invalid/stale/recovered IMU and thermal data; camera no-device, open-failure, stale and shutdown paths.
2. Failure/resource: unconfigured or unverified I²C candidates remain inactive; configured, identity-verified readers have one bounded worker with error/reconnect handling. Frame/breadcrumb/raw buffers are bounded, and camera has one worker/reconnect loop.
3. Safety/truthfulness: no IMU/thermal/camera/GNSS/map import path reaches controller, ESP32 command generation, motor output, PV-SOE authority, verification authority or E-stop. Simulations retain `SIMULATION` sources.

## Remaining physical work

Perform the documented read-only BNO055, MLX90640 and camera bring-up procedures with traction disabled. Hardware identity, electrical compatibility, live sample quality, calibration and mounting remain hardware-pending; only captured identity evidence may enable the existing read-only I²C workers.

## Verification

| Check | Result |
| --- | --- |
| Backend, including GNSS/camera/IMU/thermal tests | 87 passed in the current full backend regression run |
| Frontend tests | 23 passed in the latest frontend regression run; this backend/document-only pass did not affect frontend code |
| TypeScript type check | passed |
| Vite production build | passed |

The MapLibre lazy chunk remains above Vite's advisory size limit, but it is still loaded only on the Map page. No physical hardware claim is made by this report.
