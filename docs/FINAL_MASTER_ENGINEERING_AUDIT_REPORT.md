# TARK SIH26007 — Final Master Engineering Audit Report

> HISTORICAL BASELINE — SUPERSEDED BY LATER RED-TEAM / CORRECTION RELEASE.
> Retained as a dated record, not current completion or protocol authority.
> Use [R1 release index](TARK_RELEASE_INDEX.md),
> [Protocol V2](ESP32_PROTOCOL_V2.md) and
> [supersession register](TARK_SUPERSESSION_REGISTER.md).

**Repository baseline:** R4 Public Release Ready

**Release classification:** **B — FINAL SOFTWARE RELEASE / DEPLOYMENT READY**

This is a final pre-hardware software release. It does not claim a public hostname, external-network operation, physical-device testing, or hardware validation.

## Architecture and safety integrity

| Item | Result | Status |
|---|---|---|
| Browser is monitoring/HMI only | No frontend control route exists; role selection remains presentation only. | VERIFIED |
| Browser-to-motor or browser-to-ESP32 direct control | API-route scan and WebSocket invalid-message tests reject this boundary. | VERIFIED |
| Traction lock | Backend commands remain zero-output and every accepted frontend snapshot requires `DISABLED_PHASE_1`. | VERIFIED |
| Public demo truth | `public_demo` startup rejects a non-simulation core configuration. | VERIFIED |
| Physical E-stop | Remains outside browser/backend authority. | SUPPORTED |

## Files inspected

Repository source tree; backend configuration, API tests and protocol code; frontend package/lock/test files; scripts; `Dockerfile`; `.dockerignore`; `render.yaml`; `.env.example`; simulation fixtures; and current deployment/release documentation.

## Surgical fixes in this audit

1. Rejected unsafe deployment profile combinations: public demo cannot select authenticated mode, and public-hardware profile cannot select public-demo access.
2. Validated CORS values: only explicit `http(s)` origins without paths are accepted; wildcard CORS is rejected.
3. Tightened public CSP so public environments allow `https:`/`wss:` but not `ws:`.
4. Rejected incoming snapshots unless their traction state is exactly `DISABLED_PHASE_1`.
5. Cleared rendered authoritative values when telemetry becomes degraded/offline, preventing stale values being displayed as current.
6. Added public prototype truth text, live telemetry announcement, visible keyboard focus, and a 320 px event-layout fix.
7. Removed the unused `TARK_PUBLIC_BASE_URL` variable to avoid a misleading deployment setting.

## Three review passes

### Pass 1 — Functional

Backend API/static frontend tests, simulation contract, WebSocket malformed-message handling, public-demo simulation lock, map fallback and stale-data handling were reviewed. The stale-data display and disabled-traction payload acceptance gaps were fixed.

### Pass 2 — Deployment/device

The compiled HMI was opened locally. It connected to same-origin telemetry with an empty browser console. Two tabs connected independently without affecting the Phase 1 lock. At actual CSS viewports from 320 through 1920 px, no document overflow remained after the mobile event-row correction. Docker/Render configuration was statically reviewed. Docker runtime execution is not available on this workstation.

### Pass 3 — Security/safety

Reviewed production transport, headers, CORS, session behavior, URL-token rejection, frontend bundle strings, API routes, browser boundary and secrets. Public mode now rejects insecure profile combinations and insecure CORS values. No committed `.env` or plausible production token appeared in the packaged source; the production frontend bundle contained neither `TARK_ACCESS_TOKEN` nor test tokens.

## Final test matrix

| Test | Result | Evidence | Status |
|---|---|---|---|
| Backend | 24 passed | `pytest -q -p no:cacheprovider` | VERIFIED |
| Frontend | 9 passed | local Vitest | VERIFIED |
| ESP32 compile | strict syntax compilation succeeds | GCC `-Wall -Wextra -Werror -fsyntax-only` | VERIFIED |
| ESP32 execution | Application Control blocked executable | no behavioral result claimed | NOT VERIFIED |
| Production build | Vite build succeeds | pinned local toolchain | VERIFIED |
| Static source audit | no production localhost/URL-token transport dependency | `rg` source audit + regression test | VERIFIED |
| Localhost HMI | local browser HMI and telemetry connected | `http://localhost:8000` | VERIFIED |
| LAN | requires a second local device/network | not exercised | NOT VERIFIED |
| Render deployment | Blueprint/Docker configuration reviewed | no account authorization | SUPPORTED |
| Public HTTPS/WSS | requires Render-assigned hostname | no hostname created | NOT VERIFIED |
| Android / iOS | physical device tests | no devices provided | NOT VERIFIED |
| External network | phone on mobile data required | no public deployment | NOT VERIFIED |
| Responsive UI | actual 320–1920 CSS viewport checks | no document overflow after fix | VERIFIED |
| Security | auth/CORS/CSP/session/static checks | 24 backend tests + bundle audit | VERIFIED |
| Traction lock | route, payload and public-demo tests | no enable path | VERIFIED |

## Deployment and limitations

Render Free Web Service support is configured as `tark-sih26007-demo` in `render.yaml`, explicitly using `plan: free`, the Docker image, provider `PORT`, `/ready` health check, and same-origin frontend/API/WebSocket serving. It is **SUPPORTED**, not deployed. A free service may sleep after inactivity and has an ephemeral filesystem; the HMI uses connecting/reconnecting/offline states and does not call unavailable telemetry live.

**NOT VERIFIED:** Docker build (local Docker runtime unavailable), actual Render deployment, assigned public URL, HTTPS/WSS through a hosting provider, second network, Android, iOS, physical ESP32 execution, USB, sensors, encoders, MDD10A, motor movement, physical E-stop and field safety validation.

## Exact procedures

### Local start

```powershell
cd "tark"
.\scripts\build_frontend.ps1
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\scripts\run.ps1
```

Open `http://localhost:8000`. It is simulation-only and traction remains disabled.

### Public deployment

1. Push the frozen repository to an administrator-controlled Git repository.
2. Create a Render Blueprint/Web Service from `render.yaml` using the free tier.
3. Preserve `TARK_ENV=public_demo` and `TARK_AUTH_MODE=public_demo`.
4. Wait for Render to generate the actual `https://…onrender.com` hostname; do not invent it.
5. Verify `/`, `/health`, `/ready`, `/api/v1/status`, page refresh and `wss://<host>/api/v1/ws` from the development PC and a phone on mobile data before upgrading public status to VERIFIED.

### Future hardware entry point

Use [HARDWARE_ARRIVAL_CHECKLIST.md](HARDWARE_ARRIVAL_CHECKLIST.md). Hardware adapters remain Phase 2/not connected; no deployment setting authorizes physical traction.

## Final status

```text
TARK SIH26007 FINAL STATUS

ARCHITECTURE: VERIFIED
SOFTWARE: VERIFIED
DEPLOYMENT: READY
PUBLIC URL: NOT CREATED — HUMAN DEPLOYMENT ACTION REQUIRED
WSS: NOT VERIFIED (same-origin HTTPS-to-WSS implementation VERIFIED)
CROSS-DEVICE: NOT VERIFIED
HARDWARE: NOT YET VERIFIED
TRACTION: DISABLED_PHASE_1
BROWSER AUTHORITY: MONITORING ONLY
RELEASE STATE: B — FINAL SOFTWARE RELEASE / DEPLOYMENT READY
```
