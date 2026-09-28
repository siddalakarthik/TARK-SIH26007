# TARK SIH26007 — Public Release Report

> HISTORICAL BASELINE — SUPERSEDED BY LATER RED-TEAM / CORRECTION RELEASE.
> Retained as a dated record, not current completion or protocol authority.
> Use [R1 release index](TARK_RELEASE_INDEX.md),
> [Protocol V2](ESP32_PROTOCOL_V2.md) and
> [supersession register](TARK_SUPERSESSION_REGISTER.md).

Release state: **DEPLOYMENT READY**. This report distinguishes verified local evidence from hosting and device checks that have not occurred.

The subsequent final master audit retained this classification and added regression coverage for public-profile authentication combinations, explicit CORS origins, public CSP WebSocket transport, secure session cookie attributes, disabled-traction payload rejection, stale-data removal, keyboard focus treatment and 320 px event-layout wrapping. See [FINAL_MASTER_ENGINEERING_AUDIT_REPORT.md](FINAL_MASTER_ENGINEERING_AUDIT_REPORT.md).

| Required item | Status | Evidence / release statement |
|---|---|---|
| Repository inspected | VERIFIED | Backend, frontend, firmware, scripts, Dockerfile, `render.yaml`, tests and deployment documentation reviewed. |
| Files changed for release pass | VERIFIED | `backend/app/main.py`, backend deployment/API tests, `frontend/src/MapView.tsx`, `frontend/src/app/OperationsApp.tsx`, and this report. |
| Deployment provider | SUPPORTED | Render Free Web Service Blueprint in `render.yaml`. |
| Free-tier status | SUPPORTED | The Blueprint is intended for Render's free service; account-side selection remains required. The service may sleep while idle. |
| Render service name | SUPPORTED | `tark-sih26007-demo` in `render.yaml`. |
| Actual public URL | NOT VERIFIED | No Render account/repository authorization was available, so no hostname was created or claimed. |
| Local URL | VERIFIED | `http://localhost:8000` using `scripts/run.ps1`. |
| LAN strategy | SUPPORTED | Same build on a Pi/edge host, reached via an administrator-configured hostname such as `tark.local`. |
| WebSocket URL strategy | VERIFIED | Same-origin `/api/v1/ws`; HTTP derives `ws://`, HTTPS derives `wss://`. |
| Authentication mode | VERIFIED | Public demo is read-only `public_demo`; future authenticated monitoring creates an HttpOnly, Secure-on-HTTPS, SameSite=Strict cookie. URL token authentication is rejected. |
| Environment variables | VERIFIED | `TARK_ENV`, `TARK_AUTH_MODE`, `TARK_ACCESS_TOKEN`, `TARK_CORS_ORIGINS`, `PORT`, and deployment-independent configuration settings are documented in `.env.example`. Simulation mode remains the reviewed `config/phase1.json` setting, not an unchecked hosting variable. |
| Backend tests | VERIFIED | 20 pytest tests after the release-pass additions. |
| Frontend tests | VERIFIED | 8 Vitest tests. |
| ESP32 test | NOT VERIFIED | The C host-test source compiles, but this workstation's Windows Application Control policy blocked execution of the newly compiled binary. No firmware behavioral-pass claim is made for this release pass. |
| Production build | VERIFIED | Vite production build succeeds from the pinned local toolchain. |
| Security test | VERIFIED | Static localhost audit, no motor route, secure deployment headers, no wildcard CORS configuration, malformed WebSocket rejection, cookie auth, rejected URL token, and public-demo simulation lock are covered. |
| Browser automated verification | VERIFIED | Local desktop browser and responsive 320–1920 px viewport checks completed during the prior hardening pass. |
| Mobile viewport result | VERIFIED | 320, 360, 390, 412, 768, 1024, 1280, 1440 and 1920 px had no horizontal overflow in browser automation. |
| Physical Android result | NOT VERIFIED | No Android device or mobile-data test was supplied. |
| Physical iOS result | NOT VERIFIED | No iOS device was supplied. |
| External-network result | NOT VERIFIED | Requires a deployed hostname and a second network/device. |

## Safety release lock

- **VERIFIED:** Traction remains `DISABLED_PHASE_1`.
- **VERIFIED:** Browser is observation/monitoring only; no browser-to-motor or browser-to-ESP32 direct-control route exists.
- **VERIFIED:** Public demo startup rejects a non-simulation configuration.
- **SUPPORTED:** Physical E-stop remains independent; it is not replaced by any web service.

## Bugs discovered and fixed in this pass

1. An authenticated WebSocket path accepted a credential in the URL query string. It now accepts only the HttpOnly session cookie and has a regression test.
2. Public-demo configuration was not explicitly rejected when its core mode was changed away from simulation. Startup now rejects that state and has a regression test.
3. The HMI map fallback did not distinguish missing configuration from an unavailable provider. It now states `MAP CONFIGURATION UNAVAILABLE` without a style configuration and `MAP OFFLINE` when the configured provider fails. Routing remains `NOT CONNECTED`.
4. Startup/wake feedback now tells the user `Connecting to TARK service…` and never presents unavailable telemetry as live.

## Remaining limitations

- **NOT VERIFIED:** Render account deployment, assigned HTTPS hostname, public WSS handshake, public refresh/reconnect and cross-device access.
- **NOT VERIFIED:** Physical hardware, real radar protocol, ESP32 USB, motor, encoder, E-stop and field safety validation.
- **SUPPORTED:** Render Free services can sleep after inactivity. The UI represents this as connecting/reconnecting/offline rather than hardware failure.
- **FUTURE:** Authenticated multi-user identity/role management. The current authenticated boundary is a deployment access token and does not confer vehicle authority.

## Exact procedures

### Restart or local development

```powershell
cd "tark"
.\scripts\build_frontend.ps1
.\scripts\test.ps1
.\scripts\run.ps1
```

Open `http://localhost:8000`. The process binds `0.0.0.0:8000` locally; production uses the platform-provided `PORT`.

### Render Free deployment (administrator action required)

1. Push this exact repository to an administrator-controlled Git repository.
2. In Render, create a Blueprint from that repository and select the free Web Service option.
3. Confirm the Blueprint name `tark-sih26007-demo` and the `public_demo`/simulation environment values in `render.yaml`.
4. Deploy. Render creates the real `https://…onrender.com` URL. Record that URL only after Render displays it.
5. Do not add any hardware credential or production access token to the public demo.

### Public URL verification (only after a URL exists)

From a desktop browser and then a phone using mobile data with Wi-Fi disabled, open the exact assigned HTTPS URL and verify:

1. `/`, `/health`, `/ready`, and `/api/v1/status` load over HTTPS.
2. Browser developer tools show a `wss://<assigned-host>/api/v1/ws` connection with no mixed-content error.
3. The dashboard says `SIMULATION`, `RESEARCH PROTOTYPE`, and `TRACTION DISABLED — PHASE 1`.
4. Refresh and reconnect retain no stale data labelled as live.
5. Record the browser/device/network used before upgrading any status in this report to VERIFIED.
