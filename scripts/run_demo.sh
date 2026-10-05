#!/usr/bin/env sh
# Local observation demo only; no device discovery, package install or process kill.
set -eu
project_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_root"
python_bin="$project_root/.venv/bin/python"
port=${1:-8000}
check_only=${2:-}
if [ -n "${TARK_DEMO_PYTHONPATH:-}" ]; then
    if [ ! -d "$TARK_DEMO_PYTHONPATH" ]; then
        echo 'TARK_DEMO_PYTHONPATH must be an existing, operator-reviewed dependency directory.' >&2
        exit 1
    fi
    export PYTHONPATH="$TARK_DEMO_PYTHONPATH${PYTHONPATH:+:$PYTHONPATH}"
fi

if [ ! -x "$python_bin" ]; then
    echo 'Project .venv is missing. Follow docs/R2_WEBSITE_RUN.md.' >&2
    exit 1
fi
if [ ! -f frontend/dist/index.html ]; then
    echo 'Build frontend/dist first; see docs/R2_WEBSITE_RUN.md.' >&2
    exit 1
fi

export TARK_ENV=development TARK_AUTH_MODE=public_demo
export TARK_ACCESS_TOKEN='' TARK_CORS_ORIGINS=''
export TARK_DATABASE_PATH="$project_root/data/database/r2_demo.db"
export TARK_GNSS_DEVICE_PATH='' TARK_RADAR_PORT='' TARK_ESP32_DEVICE_PATH=''
export TARK_ESP32_BAUD='' TARK_CAMERA_DEVICE_PATH=''
export TARK_IMU_I2C_ADDRESS='' TARK_THERMAL_I2C_ADDRESS=''
export TARK_ENABLE_BROWSER_CAMERA=false TARK_GNSS_RAW_LOG_ENABLED=false
export TARK_GNSS_RAW_LOG_PATH='' TARK_ROUTE_PROVIDER_URL='' TARK_REVERSE_GEOCODER_URL=''

"$python_bin" -c '
import json, socket, sys
import fastapi, uvicorn, cbor2
with open("config/phase1.json") as stream:
    cfg = json.load(stream)
if cfg.get("mode") != "simulation" or cfg.get("hard_cap_mps") != 0:
    raise SystemExit("Demo requires simulation mode and zero hard cap; configuration was not changed")
if cbor2.loads(cbor2.dumps({"demo": True})) != {"demo": True}:
    raise SystemExit("CBOR dependency roundtrip failed; server was not started")
try:
    port = int(sys.argv[1])
except (IndexError, ValueError):
    raise SystemExit("Port must be an integer in 1024..65535")
if not 1024 <= port <= 65535:
    raise SystemExit("Port must be 1024..65535")
with socket.socket() as listener:
    listener.bind(("127.0.0.1", port))
' "$port"

if [ "$check_only" = '--check-only' ]; then
    echo "Demo preflight passed for http://localhost:$port. No server started."
    exit 0
fi
echo "TARK local demo: http://localhost:$port"
echo 'Simulation only. Hardware adapters disabled. Traction DISABLED_PHASE_1.'
echo 'Press Ctrl+C to stop. This is not a public or LAN deployment.'
exec "$python_bin" -m uvicorn app.main:app --app-dir "$project_root/backend" --host 127.0.0.1 --port "$port"
