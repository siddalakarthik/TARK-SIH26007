# TARK SIH26007 — R9 Map, Camera and Software Fix Report

> HISTORICAL BASELINE — SUPERSEDED BY LATER RED-TEAM / CORRECTION RELEASE.
> Retained as a dated record, not current completion or protocol authority.
> Use [R1 release index](TARK_RELEASE_INDEX.md),
> [Protocol V2](ESP32_PROTOCOL_V2.md) and
> [supersession register](TARK_SUPERSESSION_REGISTER.md).

## Release boundary

This is a software-only, research-prototype presentation and integration pass. Traction remains `DISABLED_PHASE_1`; motor outputs remain zero; the web application remains monitoring-only. No physical sensor, motor, encoder, E-stop, GNSS, camera, ESP32 or LD2450 claim is made by this release.

## Implemented changes

- The MapLibre map uses the configured vector style when present and otherwise uses OpenFreeMap Liberty. It begins at an India overview without claiming a vehicle position.
- Browser geolocation is initiated only by the operator's **Locate me** action. The marker, popup and status explicitly say **DEVICE LOCATION — NOT TARK VEHICLE**. Device coordinates stay in the browser UI and are not fed into the backend decision chain.
- Device follow uses `watchPosition`; a map drag stops follow. The accuracy ring is calculated from browser-reported accuracy, not a made-up radius.
- A typed vehicle-location API contract exists at `GET /api/v1/vehicle-location`. It currently returns `NOT_CONNECTED` with no location, reserving vehicle GNSS for a verified hardware source.
- Reverse-geocoding and routing are typed provider interfaces. They are disabled by default. Requests return HTTP 503 when no approved server-side provider URL is configured; the frontend retains coordinates and states the service is unavailable rather than guessing an address or drawing a route.
- A provider-returned route is drawn as a MapLibre GeoJSON line only after a configured provider responds with real geometry. Routes remain advisory and outside the safety decision loop.
- Local LD2450 target X/Y remains in a labelled local vehicle-relative radar overlay. It is deliberately not mixed with geographic coordinates.
- The RGB camera endpoint returns typed metadata only, with a separate stream endpoint reserved for future Pi/UVC integration. In the current configuration it reports `NOT_CONNECTED — PHASE 2`; it contains no image/frame payload. Browser camera preview remains development-only, opt-in, local, and explicitly not a vehicle camera.
- The driver dashboard now has a compact observation overview that shows radar, RGB, thermal and IMU states without inventing live imagery or hardware health.

## Configuration

The following optional variables are intentionally blank in `.env.example`:

```text
TARK_REVERSE_GEOCODER_URL=
TARK_ROUTE_PROVIDER_URL=
```

Configure them only after the operator has selected a provider and reviewed privacy, cost, rate-limit and key-handling requirements. Provider keys, if any, remain server-side and are not bundled into the frontend. Map style configuration is display-only and separate from core safety software.

## Verification

Executed locally on 2026-09-16:

| Check | Result |
| --- | --- |
| Python backend/API suite | 33 passed |
| React/Vitest suite | 17 passed |
| TypeScript production compilation | passed |
| Vite production build | passed |
| Default route/reverse-provider boundary | tested: HTTP 503, no fabricated output |
| Camera metadata/stream boundary | tested: not connected, no JSON frame payload, stream HTTP 503 |

The frontend build emits MapLibre as a lazy-loaded chunk. Vite reports that its map chunk is above its default 500 kB advisory threshold; it is deferred until the Map page is opened and is a performance follow-up, not a functional failure.

## Deliberately unverified or unavailable

- Actual browser location permission and camera permission were not requested during automated review.
- Reverse geocoding and route geometry are unavailable until an approved provider is configured.
- Vehicle GNSS hardware and real geographic vehicle location are not connected.
- Raspberry Pi UVC discovery, real frame acquisition, camera stream transport and camera calibration are not verified.
- Real LD2450 frame decoding, ESP32 USB, MDD10A, motors, encoders, thermal, IMU and physical E-stop remain hardware-dependent.

## Operator checks when hardware arrives

1. Keep traction disabled and disconnect motor power while validating Pi/ESP32/camera/GNSS discovery.
2. Verify the real device identity and timestamps before enabling each adapter configuration.
3. Validate vehicle GNSS against a controlled surveyed location; never substitute browser location.
4. Verify UVC video locally, then validate the dedicated stream endpoint, frame age and dropout handling.
5. Validate any third-party geocoder/route provider independently. Neither service may be used as a safety input.
