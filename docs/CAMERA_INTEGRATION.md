# Pi/UVC Camera Integration — Logitech C920s or Equivalent

## Scope

The target is a Logitech C920s or equivalent UVC RGB camera connected to the Raspberry Pi. The implemented adapter is designed and software-tested; it is not physically connected, identified, calibrated or verified. Camera data is observation-only and has no path to PV-SOE, ESP32 commands, motors or E-stop.

## Architecture

`PiUvcCameraAdapter` uses an optional OpenCV/V4L2 worker: configured device → one capture thread → JPEG encode → bounded latest-frame buffer → camera metadata → optional MJPEG endpoint. It never opens a camera automatically. `TARK_CAMERA_DEVICE_PATH` must name an explicitly selected, physically verified device. Discovery only reports `/dev/video*` candidates as `IDENTITY_UNVERIFIED`; it does not infer a C920s from a path.

## States and sources

The real adapter reports `NOT_CONNECTED`, `DEVICE_DETECTED`, `OPENING`, `ONLINE`, `STALE`, `DROPPED` or `ERROR`. Its real source is `PI_UVC`; fixture/simulation and replay sources are labelled separately. Browser development preview remains local to the browser, requires an explicit user action, and is never the vehicle camera.

## Configuration

`.env.example` includes device path, preferred width/height/FPS, stale timeout, stream FPS and JPEG quality. Preferred configuration is a request, not a capability claim: the actual selected capture dimensions/FPS are reported only from the opened device. Install `.[camera]` for optional `opencv-python-headless`; ordinary simulation installs do not need it.

## Streaming and diagnostics

When a real fresh Pi/UVC frame exists, `/api/v1/cameras/vehicle-rgb/stream` serves bounded-rate MJPEG. The status endpoint reports source, state, frame age, dimensions, selected FPS, pixel format, sequence, dropped frames and backend. No image bytes are inserted into status JSON. Without a fresh real frame, the endpoint returns `503 CAMERA NOT CONNECTED`.

Repeated read failures transition through `DROPPED`, release the capture after `TARK_CAMERA_FAILURE_THRESHOLD`, expose an error/reconnect count, wait for the bounded reconnect interval, then re-open. A successful frame resets the failure counter. This worker is dormant unless explicitly started after device identity verification.

## Hardware bring-up

1. Keep traction disabled and motor power disconnected.
2. Connect the camera to the Pi and enumerate candidates.
3. Identify the exact camera using OS tools; set the selected `TARK_CAMERA_DEVICE_PATH`.
4. Start read-only capture, inspect actual dimensions/FPS/pixel format and frame age.
5. Test disconnection, close, deliberate restart and MJPEG observation.
6. Validate mounting/calibration separately before any future perception work.

## Still requiring physical verification

USB identity, UVC compatibility, V4L2 profiles, actual resolution/FPS, CPU cost, frame latency, disconnect recovery, optics, lighting and calibration are all physical verification work. No object detection or scene-safety claim is implemented.
