# TARK SIH26007 — Final Public Access Release Report

> HISTORICAL BASELINE — SUPERSEDED BY LATER RED-TEAM / CORRECTION RELEASE.
> Retained as a dated record, not current completion or protocol authority.
> Use [R1 release index](TARK_RELEASE_INDEX.md),
> [Protocol V2](ESP32_PROTOCOL_V2.md) and
> [supersession register](TARK_SUPERSESSION_REGISTER.md).

**Release:** R5, public-access handoff update

**Result:** **DEPLOYMENT READY — HUMAN ACCOUNT AUTHORIZATION REQUIRED**

## Deployment result

| Item | Result | Status |
|---|---|---|
| Deployment provider | Render Web Service | SUPPORTED |
| Free-tier configuration | `render.yaml` explicitly sets `plan: free` | VERIFIED |
| Git repository / remote | This workspace is not a Git repository and has no remote | NOT VERIFIED |
| GitHub/GitLab/Bitbucket deployment credentials | No CLI credentials/tooling available | NOT VERIFIED |
| Render account session | Render dashboard opened at the sign-in page; no authenticated session exists | NOT VERIFIED |
| Actual public URL | No Render service was created | NOT CREATED |
| HTTPS and public WSS | Require the assigned Render hostname | NOT VERIFIED |
| Cross-device / Android / iOS / external network | Require a public URL and physical devices | NOT VERIFIED |

## Verified public-access implementation

- One same-origin React/FastAPI application serves the HMI, REST and `/api/v1/ws`.
- Public HTTPS pages derive `wss://<current-host>/api/v1/ws`; local HTTP derives `ws://` only in non-public environments.
- Render container command binds `0.0.0.0:${PORT:-10000}` and serves `/ready` for health checks.
- `public_demo` requires simulation configuration and public-demo access mode.
- `render.yaml` requests the free service plan, Docker runtime and `/ready` health check.
- Public demo remains simulation/read-only/monitoring-only. Traction remains `DISABLED_PHASE_1`.
- Persistent UI labels state `SIMULATION`, `RESEARCH PROTOTYPE`, `NOT PHYSICALLY VALIDATED`, and `TRACTION DISABLED — PHASE 1`.
- Browser indicators expose CONNECTING, CONNECTED, DEGRADED, RECONNECTING and OFFLINE. Degraded/offline telemetry clears rendered authoritative values.
- Map configuration/provider failures remain isolated as `MAP CONFIGURATION UNAVAILABLE` or `MAP OFFLINE`; routing is `NOT CONNECTED`.

## Current evidence

- **25 backend tests passed.**
- **9 frontend tests passed.**
- **Vite production build passed.**
- **ESP32 source strict compilation passed.** Behavioral host executable execution remains not verified because Windows Application Control blocks generated executables.
- **Render Blueprint static validation passed** for Docker runtime, `plan: free`, `/ready`, and the public-demo profile.
- **Local HMI, two-tab operation and responsive 320–1920 px checks were verified.**

## Single remaining human action

Sign in to a Render account and connect an administrator-controlled Git repository containing this frozen release. The repository must first be pushed to GitHub, GitLab or Bitbucket because Render Blueprints deploy from a repository.

Then, in Render:

1. Create a **Blueprint** from that repository’s `render.yaml`.
2. Keep `tark-sih26007-demo` if Render accepts the name; otherwise let Render require a unique suffix and record the actual hostname it creates.
3. Confirm the free plan and deploy.
4. Copy the exact generated `https://…onrender.com` URL only after it appears in the Render dashboard.
5. Verify `/`, `/health`, `/ready`, `/api/v1/status`, browser refresh and `wss://<actual-host>/api/v1/ws` from a second network/device before marking public access verified.

Render documents the Blueprint `plan: free` field, Docker runtime, health checks and public `onrender.com` service hostnames in its [Blueprint reference](https://render.com/docs/blueprint-spec) and [free deployment guide](https://render.com/docs/free).

## Status

```text
TARK SIH26007 FINAL STATUS

ARCHITECTURE: VERIFIED
SOFTWARE: VERIFIED
LOCAL URL: VERIFIED
PUBLIC DEPLOYMENT: BLOCKED
PUBLIC URL: NOT CREATED
HTTPS: NOT VERIFIED
WSS: NOT VERIFIED
CROSS-DEVICE: NOT VERIFIED
ANDROID: NOT VERIFIED
IOS: NOT VERIFIED
SIMULATION: ENABLED
TRACTION: DISABLED_PHASE_1
BROWSER AUTHORITY: MONITORING ONLY
HARDWARE: NOT YET VERIFIED
RELEASE STATE: DEPLOYMENT READY — HUMAN ACCOUNT AUTHORIZATION REQUIRED
```
