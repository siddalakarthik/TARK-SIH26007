# V9 Prompt 3 — Pi/UVC Camera and GNSS/Map Audit Report

## Existing camera foundation

Before this pass the dashboard had a truthful camera placeholder, metadata route and an isolated browser-development preview. No Pi capture transport or usable stream existed.

## Implemented camera software

- Added a dormant `PiUvcCameraAdapter` with explicit device selection, Linux candidate discovery, one worker thread, OpenCV/V4L2 optional transport, requested profile negotiation, JPEG encode, latest-frame-only buffering, sequence/drop diagnostics, stale detection and clean stop.
- Added status, capability and MJPEG stream endpoint behavior. A stream is available only from a fresh frame; status remains metadata-only.
- Added optional `.[camera]` dependency and all camera settings to `.env.example`. Normal simulation installs do not require OpenCV.
- Preserved browser preview as local, opt-in `DEVELOPMENT BROWSER CAMERA`, never vehicle telemetry.

## GNSS and map corrections

- Fixed GNSS internal state to transition to `STALE` together with the API response and recover to `ONLINE` only after a fresh accepted fix.
- Kept UTC measurement time distinct from local monotonic receive time.
- Corrected GGA interpretation: altitude is no longer treated as evidence of a 3D fix. RMC/GGA aggregation now permits small coordinate rounding differences but rejects incompatible receive epochs/sources.
- Fixed MapLibre style-load timing so a device or vehicle update that arrives before the style is ready is applied after readiness, without creating a second map or socket.

## Three audit passes

1. **Functional:** mocked UVC open failure, discovery, frame fixture, stale/stop behavior, GNSS stale recovery, stream contract and API compatibility checked.
2. **Resource/performance:** camera and GNSS each use at most one worker; frame/raw/breadcrumb buffers are bounded; browser media tracks are stopped on panel unmount; MapLibre remains lazy-loaded. The large MapLibre Vite chunk is an advisory performance follow-up.
3. **Safety/truthfulness:** repository search found no camera/GNSS/map imports into controller, ESP32, motor, PV-SOE, verification or E-stop code. Browser device location remains distinct from vehicle location. Simulated fixture frames are labelled `SIMULATION` and never receive a real-hardware claim.

## Verification

| Suite | Result |
| --- | --- |
| Backend | 42 passed |
| Frontend | 17 passed |
| TypeScript | passed |
| Production build | passed |

## Physical dependencies remaining

The C920s/equivalent is not connected, identified, opened, profiled, streamed, calibrated or performance-tested. LC29H(AA) hardware is similarly not connected or verified. Keep traction disabled throughout both bring-up workflows. The next prompt should use captured read-only device discovery/probe evidence to add an explicit verified-device selection policy; it must not infer identity from `/dev/video*` or serial-port names.
