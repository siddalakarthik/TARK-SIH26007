# TARK Phase 1 Backend

This repository implements the Phase 1 Raspberry Pi software chain for the TARK SIH26007 research prototype. Phase 1 uses a real or simulated HLK-LD2450 source, deterministic decision processing, USB command framing, logging, replay and an observation-only FastAPI service. It deliberately does not energize traction or expose a motor-control API.

The real LD2450 serial adapter captures raw bytes and handles open/timeout/disconnect. Its vendor binary frame decoder is intentionally not claimed implemented because the exact vendor frame specification was not supplied in the project authority. The simulation/replay decoder is fully deterministic and uses the explicit `SIM1` fixture format. Add a vendor-reviewed decoder before enabling real normalized detections.

Prompt 3.1 adds simulation-first interfaces for radar, ESP32, MDD10A, encoders, camera, thermal sensor and IMU, plus the React/TypeScript operations UI source. Every Phase 2 interface reports simulation or not-connected status until hardware verification. See `docs/HARDWARE_ARRIVAL_CHECKLIST.md` before connecting devices.

## Quick start

```powershell
python -m pip install -e ".[dev]"
$env:PYTHONPATH = "backend"
python -m app.main
pytest -q
```

## Operations UI

```powershell
cd frontend
pnpm install
pnpm build
pnpm test
cd ..
scripts\run.ps1
```

Open `http://localhost:8000`. FastAPI serves the compiled frontend and API from one origin. The Map view defaults to the no-key OpenFreeMap Liberty style and starts at an India overview when no approved display location is configured. Set `VITE_MAP_STYLE_URL` for an approved alternate style (or legacy `VITE_MAPTILER_STYLE_URL`); map and route output are advisory and never motion authority. A radar target stays in its local X/Y metre scope and is never portrayed as a geographic location. Set `TARK_DEFAULT_MAP_CENTER=longitude,latitude` only after an approved display location exists.

Browser location is requested only by the `Locate me` operator action and is labelled **DEVICE LOCATION — NOT TARK VEHICLE**. It is not uploaded or used by the decision engine. Vehicle GNSS is a separate, currently not-connected hardware contract. Optional reverse geocoding and routing are server-side provider boundaries: configure `TARK_REVERSE_GEOCODER_URL` and `TARK_ROUTE_PROVIDER_URL` only after approving provider/privacy terms. With either unset, the UI says unavailable and never fabricates an address or route. Vehicle camera data uses a metadata endpoint and a separate future stream endpoint; no frames are carried inside status JSON.

## Portable deployment

The frontend uses same-origin API and WebSocket URLs, so one unchanged build supports local development, an edge hostname, and an HTTPS public hostname. See [public deployment](docs/PUBLIC_DEPLOYMENT.md) for local/LAN use, Render container deployment, custom domains, authenticated monitoring, and the optional Cloudflare Tunnel edge pattern. Public deployment does not enable hardware or traction.

The service exposes `/health`, `/api/v1/status`, `/api/v1/tracks`, `/api/v1/events`, `/api/v1/runs`, and observation/replay endpoints. There is no command-to-motor endpoint.

The final pre-hardware audit is recorded in [docs/FINAL_MASTER_ENGINEERING_AUDIT_REPORT.md](docs/FINAL_MASTER_ENGINEERING_AUDIT_REPORT.md). Its release classification is **B — FINAL SOFTWARE RELEASE / DEPLOYMENT READY**: local evidence is complete, while a real Render hostname, external network, physical mobile devices and hardware remain explicitly unverified.

The public-access handoff is recorded in [docs/FINAL_PUBLIC_ACCESS_RELEASE_REPORT.md](docs/FINAL_PUBLIC_ACCESS_RELEASE_REPORT.md). Render was reachable only at its sign-in page from this workspace, and this folder has no Git remote; consequently no public URL has been created or claimed.

The controlled pre-hardware completion report is [docs/FINAL_PRE_HARDWARE_SOFTWARE_COMPLETION_REPORT.md](docs/FINAL_PRE_HARDWARE_SOFTWARE_COMPLETION_REPORT.md).

The R9 map, camera and truthful-status review is [docs/FINAL_R9_MAP_CAMERA_SOFTWARE_FIX_REPORT.md](docs/FINAL_R9_MAP_CAMERA_SOFTWARE_FIX_REPORT.md).
