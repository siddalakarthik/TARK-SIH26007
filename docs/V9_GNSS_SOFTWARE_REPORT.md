# V9 Vehicle GNSS and Live Map Software Report

> HISTORICAL BASELINE — SUPERSEDED BY LATER RED-TEAM / CORRECTION RELEASE.
> Retained as a dated record, not current completion or protocol authority.
> Use [R1 release index](TARK_RELEASE_INDEX.md),
> [Protocol V2](ESP32_PROTOCOL_V2.md) and
> [supersession register](TARK_SUPERSESSION_REGISTER.md).

## Existing foundation reused

R9 already provided the India-first MapLibre map, browser-device location separation, a server-side reverse-geocoder and route-provider boundary, local-frame radar overlay, and an observation-only HMI. The former vehicle-location endpoint truthfully returned no connected receiver.

## Implemented

- `app.gnss` provides one normalized `GnssFix` contract, configurable health thresholds, checksum-validated RMC/GGA parsing, monotonic timestamps, freshness, plausibility rejection, bounded breadcrumbs, discovery state, deterministic simulation, and replay-compatible ingestion.
- The vehicle endpoint now returns an explicit `NO_RECEIVER`/`SEARCHING`/`NO_FIX`/`ONLINE`/`STALE`/`ERROR` response with no coordinate until the service accepts a valid fix.
- The existing WebSocket emits `location_update` using the same socket; no second WebSocket manager was created.
- The map can render a separate TARK vehicle marker/trail from normalized vehicle GNSS. Browser device location remains separate and cannot be passed to vehicle location.
- LC29H(AA) configuration, physical arrival procedure, safety isolation and remaining verification work are documented in `GNSS_INTEGRATION.md`.

## Safety review

`app.gnss` has no imports from controller, ESP32 protocol, motor driver, verification, PV-SOE or E-stop code. Location is a status/map payload only. Browser device geolocation remains local to the browser and never reaches `/api/v1/vehicle-location`.

## Verification

| Check | Result |
| --- | --- |
| Backend/API/safety tests | 35 passed |
| GNSS-specific tests | 2 files, 5 tests passed |
| Frontend Vitest | 17 passed |
| TypeScript type check | passed |
| Vite production build | passed |

The MapLibre lazy chunk is above Vite's default advisory size threshold but is deferred until opening the map. This is a performance follow-up, not a functional failure.

## Physical work remaining

LC29H(AA) USB enumeration, actual receiver identity, exact stream/baud, active antenna performance, real accuracy, real-world dropout behavior and installation validation are not verified. Traction remains disabled throughout initial GNSS integration.

## Prompt 2 hardware-ready extension

The serial boundary is now implemented in `app.gnss_driver`: configurable optional-pyserial opener, discovery candidates, one threaded reader, bounded framing/raw diagnostics, corrupt/oversized-line handling, RMC/GGA aggregation, reconnect delay and clean shutdown. `python -m app.gnss_probe --device <verified-device-path>` is a read-only bring-up tool. The final serial device identity and actual LC29H(AA) output remain physically unverified. Backend verification after this extension: **37 passed**.
