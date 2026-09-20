# TARK SIH26007 — Final Pre-Hardware Software Completion Report

**Date:** 2026-09-15  
**Classification:** research prototype; not mine-certified; not a safety-certified motion system.

## Release outcome

The complete pre-hardware software system is ready for controlled simulation, replay, local monitoring and integration preparation. Phase-1 traction remains disabled. No physical motor, MDD10A, encoder, ESP32 USB, camera, thermal sensor, IMU, LD2450 decoder or E-stop validation is claimed.

## This completion pass

- The Map view now starts with the no-key OpenFreeMap Liberty style. Style priority is `VITE_MAP_STYLE_URL`, legacy `VITE_MAPTILER_STYLE_URL`, then OpenFreeMap.
- A geographic centre is optional. `TARK_DEFAULT_MAP_CENTER=longitude,latitude` and `TARK_DEFAULT_MAP_ZOOM` only control display. With no centre, the HMI presents a labelled neutral world view and does not invent GPS or routes.
- Radar tracks remain in a dedicated local `X/Y` metre scope. No radar coordinate is converted into longitude/latitude.
- Settings is an explicit, read-only route with System, Map, Display, Connection, Simulation and About panels. It has no safety override, motor command, configuration editor or credential display.
- Map failure stays advisory: the local safety pipeline continues and the HMI presents `MAP OFFLINE`/configuration status without describing the system as safe.
- The ESP32 project now includes software-only MDD10A and encoder boundaries. The MDD10A boundary clamps an input request and still applies zero output under `DISABLED_PHASE_1`; the encoder boundary is simulation/host-test only and reports wheel response, never ground speed.

## Validation evidence

| Pass | Evidence | Result |
|---|---|---|
| Functional | backend API, WebSocket, simulation/replay and map-safety source tests | passed locally |
| UI | 12 TypeScript tests, Vite production build, all eight HMI routes at 1024 px, map/settings visual inspection at 320/1024/1920 px | passed locally |
| Communication readiness | protocol/CRC/supervisor and safe ESP32 boundary source compilation plus host executable | passed locally; physical USB is unverified |
| Security/deployment | same-origin transport, CSP source, Render blueprint and credential-source tests | passed locally |

The consolidated test commands and limits are in `docs/TEST_REPORT.md`. Browser-responsive checks found and corrected a document-level mobile overflow; the intentionally horizontally scrollable mobile navigation remains local to the navigation strip. Actual remote map tiles remain subject to the operator's network and the provider's availability.

## Explicit pending hardware work

1. Review actual ESP32-S3 DevKitC-1 documentation, enumerate USB, flash firmware and verify STATUS with outputs still disabled.
2. Capture and review the purchased LD2450 vendor protocol before accepting real normalized detections.
3. Verify MDD10A model/terminals and encoder supply/interface against the released schematic and purchased documentation before any GPIO binding.
4. Discover and timestamp-test actual camera, MLX90640 and BNO055 hardware before reporting them as connected.
5. Perform physical E-stop, traction isolation, braking and environmental validation independently of this software.

## Final status

- Software: complete for simulation/replay/local monitoring and integration preparation.
- Physical hardware: not yet integrated or verified.
- Traction: disabled Phase 1.
- Safety parameters: parameterized, not validated.
- Deployment: locally packaged; no public URL is claimed.
