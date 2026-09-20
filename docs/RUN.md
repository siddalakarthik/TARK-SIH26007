# Run

From `tark`, create a local environment, install dependencies, build the frontend, then start the one-URL application:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\scripts\build_frontend.ps1
.\scripts\run.ps1
```

Open `http://localhost:8000`. The script performs a virtual-environment, dependency, compiled-frontend and port-8000 preflight before it starts Uvicorn. It reports the owning PID/process instead of killing a process already bound to port 8000. `http://localhost:8000/health` reports `DISABLED_PHASE_1`; the service does not provide a motor-command endpoint. Use `config/phase1.json` for the default mode, or start Uvicorn through `python -m app.main --mode simulation|replay|real_radar` when an explicitly reviewed runtime mode is required. Do not select `real_radar` normalized processing until a vendor-reviewed LD2450 binary frame decoder has been added.
