# TARK SIH26007 — Final Pre-Hardware Software Polish Report

**Date:** 2026-09-15  
**Release:** R8 final pre-hardware software polish  
**Classification:** research prototype; not mine-certified; browser monitoring only.

## Bugs discovered and corrected

1. The map defaulted to a neutral world location that did not fit the Indian project context. It now defaults to the OpenFreeMap Liberty **India overview** (`78.9629, 20.5937`, zoom `4.2`) when no approved display centre is configured. This is explicitly not a mine or vehicle location.
2. Map readiness used the full-load event, which could leave the UI in `MAP LOADING` while an already usable style was rendering. It now marks `MAP AVAILABLE` at MapLibre style readiness and continues to report provider errors as `MAP OFFLINE`.
3. The sensor readiness renderer assumed all health objects used `device_id`; radar health exposed `sensor_id`. The backend now normalizes the public snapshot to `device_id`, and the HMI has a defensive fallback. A browser-console error was eliminated and covered by regression tests.
4. Mobile layout was rechecked across nine widths; no document-level horizontal overflow remains. The navigation strip alone is intentionally horizontally scrollable on narrow screens.

## Map and location

- MapLibre and no-key OpenFreeMap Liberty remain the default; override order is `VITE_MAP_STYLE_URL`, legacy `VITE_MAPTILER_STYLE_URL`, then OpenFreeMap.
- Map controls provide India overview, world view, standard map controls, `LOCATE ME`, and optional follow-device mode.
- Browser location is collected only after a user action, held locally in the browser, and displayed as **DEVICE LOCATION** with latitude, longitude and reported accuracy. It is never submitted to TARK, treated as a vehicle location, or mixed with radar.
- Geolocation permission is intentionally allowed by `Permissions-Policy`; camera remains denied by default.
- Radar stays in a strictly separate **RADAR LOCAL FRAME** with X/Y metres. No radar-to-GPS conversion exists.

## Camera, thermal and IMU readiness

- A defined `CameraFrameMetadata`/camera health boundary now represents source ID, source mode, state, timestamp/freshness, resolution, frame rate and error reason without storing frames in application state.
- The Sensor page distinguishes vehicle RGB camera, thermal camera, IMU, encoders, ESP32 and MDD10A software boundaries from hardware state. It reports **SOFTWARE INTERFACE READY** and **HARDWARE NOT CONNECTED** rather than implying future software work.
- A development-only **BROWSER CAMERA PREVIEW** is implemented. It is disabled by default (`TARK_ENABLE_BROWSER_CAMERA=false`), requests permission only after a button click, uses no audio, never uploads frames or calls the backend, labels itself not a vehicle camera, and stops tracks on close/unmount.
- Future Pi UVC, MLX90640 and BNO055 adapters remain truthful: hardware/physical calibration is not verified.

## ESP32, Pi and vehicle-interface readiness

- Pi-side abstractions, deterministic simulation, health interfaces and USB/ESP32 protocol boundaries remain ready for integration.
- ESP32 firmware now includes protocol, CRC, sequence/expiry/heartbeat supervisor, status, safe motor and encoder boundaries, plus a software watchdog boundary. Physical ESP-IDF watchdog registration is intentionally pending board/scheduler verification.
- MDD10A requests are clamped in the software boundary but always apply zero under `DISABLED_PHASE_1`. There is no browser motor-control route.
- Encoder terminology remains wheel response, not ground-truth speed; VCC/interface remains TBD/VERIFY.

## Navigation, performance and safety

- The persistent application shell owns the WebSocket, snapshot, role and connection state. Page changes do not reload the document or create page-specific sockets.
- Map remains lazy loaded; its instance is cleaned up on page unmount, while device-location watches are cleared when leaving the Map view.
- Event display is bounded to the newest 100 events. No video frames or base64 payloads enter React state.
- Settings remains read-only with System, Map, Display, Connection, Simulation and About. It contains no PWM, motor, E-stop, traction or ESP32-command controls.

## Five-pass validation

| Pass | Result |
|---|---|
| Functional | navigation, snapshot contract and sensor contract defect found, fixed and retested |
| Map/GIS | India default, device-location UI states, local radar separation, map readiness and controls checked |
| Camera/sensor readiness | camera policy, no-upload design, disabled default, cleanup test and readiness labels checked |
| Performance/navigation | shell navigation, bounded events, lazy map, responsive 320–1920 px and no page overflow checked |
| Security/safety/regression | no browser motor authority, default camera denial, explicit geolocation only, CSP, tests and host firmware test checked |

## Evidence

- Backend: **30 passed**.
- Frontend: **17 passed**; production build passed.
- ESP32 host protocol/safety test: passed, including watchdog-boundary checks.
- Local rebuilt runtime: `/health` returned `ready`, `SIMULATION`, `DISABLED_PHASE_1`; diagnostics returned India overview and browser camera preview disabled.

## Remaining physical and deployment work

- Hardware discovery, flashing, USB enumeration, real LD2450 frame verification, UVC/thermal/IMU discovery, encoder interface verification, MDD10A/motor commissioning and independent physical E-stop testing remain hardware-only work.
- Browser device location is not verified in this release because granting a real device-location permission was intentionally not automated; permission-denied/unavailable states are implemented and unit-tested.
- No public URL is created. External deployment still requires administrator authorization, account/repository connection and HTTPS/WSS verification.

## Final status

| Area | Status |
|---|---|
| Software stack | VERIFIED |
| Dashboard | VERIFIED |
| Map / India-first map | VERIFIED |
| Device location | IMPLEMENTED; real permission/device result not verified |
| Camera / thermal / IMU software | READY |
| ESP32 / MDD10A / encoder / Pi↔ESP32 software | READY |
| Simulation | VERIFIED |
| Physical hardware | NOT YET VERIFIED |
| Public URL | NOT CREATED — external deployment authorization required |
| Traction | DISABLED_PHASE_1 |
| Browser authority | MONITORING ONLY |
