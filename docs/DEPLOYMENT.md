# Deployment Preparation

Windows development: create `.venv`, install backend dependencies, run `scripts/build_frontend.ps1`, `scripts/test.ps1`, then `scripts/run.ps1`. `scripts/test_frontend.ps1` uses the installed, pinned local Vitest binary and therefore does not contact the registry. FastAPI serves `frontend/dist` at the same URL. The startup script checks the project environment, backend imports, compiled frontend and port 8000 before it starts Uvicorn; it reports (but never kills) a process already using the port. The backend listens at `http://localhost:8000`; production target is `http://tark.local:8000` when Raspberry Pi hostname/network configuration is set.

Raspberry Pi target: install Python environment, configured service account, writable data directories, backend package, compiled `frontend/dist`, and a system service running Uvicorn. The core decision loop starts offline. MapTiler/OpenRouteService are optional display/provider adapters; do not make startup depend on them. Build the frontend in a controlled network-enabled development environment, then deploy only the compiled `frontend/dist` and pinned source/lockfile—not `node_modules`.

For universal-access profiles, public HTTPS hosting, authentication boundary, dynamic platform ports, custom domains, and the optional edge tunnel pattern, see [PUBLIC_DEPLOYMENT.md](PUBLIC_DEPLOYMENT.md).
