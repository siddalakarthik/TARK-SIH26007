# TARK R2 website — local demonstration guide

3 October 2026 · Software demonstration · Hardware not physically verified

## What this run does

The existing FastAPI application serves the compiled React interface and the API from one origin. Use the new `scripts/run_demo.ps1` or `scripts/run_demo.sh` for a local demonstration. They do not replace the existing deployment scripts.

The launchers:

- Require `config/phase1.json` to contain `mode: simulation` and `hard_cap_mps: 0`; they refuse to change an incompatible configuration.
- Clear the configured physical GNSS, radar, camera, ESP32 and I2C selections for the server process.
- Disable browser-camera preview, raw GNSS logging and optional remote route/geocoder providers.
- Bind only `127.0.0.1`, not the LAN or internet.
- Use `data/database/r2_demo.db`, separate from the default application database.
- Refuse an occupied port without killing its owner.
- Leave traction `DISABLED_PHASE_1`. No screen is a motor controller, physical E-stop or certified safety device.
- Restore overridden process environment variables when the PowerShell launcher finishes.

The process runs in `development` with local `public_demo` access so recording/replay controls can be exercised on the local computer. This is deliberately **not** a public deployment. Do not expose this unauthenticated development service through a tunnel or router.

## Windows: existing prepared project

Run from the `tark` repository root:

```powershell
.\scripts\build_frontend.ps1
.\scripts\run_demo.ps1
```

Open **http://localhost:8000/**. Press Ctrl+C in the server terminal to stop it.

The startup script does not install packages. The build script uses the already installed TypeScript and Vite when available; if dependencies are missing, its existing workflow invokes the lockfile-controlled package install.

### This workstation's optional pure-Python CBOR runtime

Windows application control blocked the native `_cbor2` extension installed in the existing `.venv`. The application source, security policy and `.venv` were not changed to suppress that error.

An official `cbor2==5.6.5` source release was built with its supported `CBOR2_BUILD_C_EXTENSION=0` option into the separate workspace directory `../work/tark_demo_python`. It satisfies the project's `cbor2>=5.6` dependency and uses the vendor's Python implementation, not a new protocol implementation.

On this workstation, explicitly select that prepared directory:

```powershell
.\scripts\run_demo.ps1 -CheckOnly -DemoPythonPath '..\work\tark_demo_python'
.\scripts\run_demo.ps1 -DemoPythonPath '..\work\tark_demo_python'
```

`-CheckOnly` imports required dependencies, checks the frozen simulation configuration and briefly checks the listening address, then exits without starting a server. A different free port can be selected with `-Port 8017`; open `http://localhost:8017/` in that case.

The optional directory is **not part of the repository release**. Another computer should use its normal supported environment; it does not inherit this workstation path. If it needs this official non-native option, an operator can reproduce the isolated install after reviewing the package source:

```powershell
$env:CBOR2_BUILD_C_EXTENSION='0'
.\.venv\Scripts\python.exe -m pip install --no-deps --no-binary=cbor2 --target '..\work\tark_demo_python' 'cbor2==5.6.5'
```

Do not disable Windows application control, unblock unknown executables, or replace the library with a hand-written encoder to make tests pass. Source: [official cbor2 5.6.5 release](https://github.com/agronholm/cbor2/tree/5.6.5).

## Linux / Raspberry Pi preparation

The software-only launcher expects `.venv/bin/python` and an already built `frontend/dist/index.html`:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
cd frontend
pnpm install --frozen-lockfile
pnpm build
cd ..
sh scripts/run_demo.sh 8000 --check-only
sh scripts/run_demo.sh 8000
```

These are setup commands, not a claim that this release was physically deployed or benchmarked on the new Pi. This task did not install camera, serial or I2C hardware packages. No hardware is needed for the demo launcher.

An optional reviewed dependency directory can be selected using `TARK_DEMO_PYTHONPATH`; it is not required for a normal working Python environment.

## Useful local addresses

| Address | Purpose |
|---|---|
| `http://localhost:8000/` | Main operator website |
| `http://localhost:8000/health` | Runtime readiness, mode and zero-traction declaration |
| `http://localhost:8000/ready` | Ready check; unavailable runtime returns an error |
| `http://localhost:8000/api/v1/status` | Authoritative current research decision and normalized observations |
| `http://localhost:8000/api/v1/flagship` | Read-only, explicitly synthetic two-participant presentation scene and hardware migration ledger |
| `http://localhost:8000/api/v1/vehicle-location` | Existing normalized location boundary |
| `http://localhost:8000/api/v1/diagnostics` | Software/configuration/deployment information |
| `http://localhost:8000/docs` | Existing FastAPI API documentation |
| `ws://localhost:8000/api/v1/ws` | Observation WebSocket used by the application, not a normal browser page |

REST uses relative URLs. WebSocket uses the current page host and changes to `wss:` when served over HTTPS. The production-style local build therefore needs no separate frontend URL and no CORS exception.

`pnpm dev` starts the existing Vite development server, normally at `http://localhost:5173`. The current repository does **not** define a Vite API/WebSocket proxy, and Vite does not start the backend. A standalone Vite page is therefore not the supported complete demonstration workflow. Build the frontend and open the one-origin FastAPI application above: `http://localhost:8000/` supplies both the website and its same-origin REST/WebSocket connections. An attempted development proxy configuration was removed after this workstation's esbuild configuration loader encountered an ancestor-directory access error; no proxy is claimed in this release.

## How to demonstrate it honestly

1. Open the dashboard and check the simulation/research labels and connection indicator.
2. Inspect the core decision and its reason. The permitted command remains zero; do not increase it to make the screen look more dramatic.
3. Open the flagship fleet/course view. Its A and B participants, route and hazard are deterministic display fixtures, not acquired positions or a surveyed mine.
4. Keep the fleet fixture distinct from the existing safety/radar simulation. The fixture is not silently fed into PV-SOE or used as evidence of cooperative collision avoidance.
5. Inspect sensor availability. The current physical camera, thermal and IMU panels may correctly be unavailable; the new BOM is not made live by changing their labels.
6. Use the existing recording/replay controls where available. Original recorded decisions and recomputation are separate evidence. The synthetic flagship display contract is not a claim of full multi-sensor fleet recording.
7. Disconnect internet if desired while retaining the local server. The local schematic course does not require a paid map key. An optional online geographic background in an existing map view still depends on its provider and must not be claimed offline.
8. Stop the server to demonstrate unavailable/reconnecting state. Old values must not masquerade as current readings.

No global address search, paid traffic feed, mine survey, autonomous routing or live physical cooperative network is claimed by the display fixture. Free mapping software does not supply surveyed mine roads automatically.

## Tests and build commands

Frontend, from `frontend` with dependencies already installed:

```powershell
node node_modules/vitest/vitest.mjs run --environment jsdom
node node_modules/typescript/bin/tsc -b
node node_modules/vite/bin/vite.js build
```

Backend, from `tark`, using this workstation's optional runtime:

```powershell
$env:PYTHONPATH=(Resolve-Path '..\work\tark_demo_python').Path
$env:PYTHONDONTWRITEBYTECODE='1'
Get-ChildItem Env:TARK_* | ForEach-Object { Remove-Item -LiteralPath ('Env:' + $_.Name) }
$testTmp=Join-Path (Resolve-Path '..\work') ('pytest_r2_'+[guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp $testTmp
```

Use a **fresh, uniquely named test temporary directory**. Pytest owns its `--basetemp`; never point it at a project, data directory or existing user folder. Run these environment-cleaning commands in a test-only terminal; they affect that terminal process, not stored system configuration. The evidence harness intentionally rejects ambient `TARK_*` configuration, even a non-empty string such as `false`.

The existing tests use fakes/fixtures for physical boundaries. Passing them establishes software behavior only. Compiled firmware host tests, if blocked by application-control policy, must be reported as blocked rather than disguised as successful hardware verification.

### Latest backend check on this workstation

On 3 October 2026 the complete suite collected 353 tests: **322 passed, 31 setup errors**, with three dependency deprecation warnings, in 52.66 seconds. All 31 errors came from the shared `test_protocol_correctness.py` firmware-host fixture when Windows returned `WinError 4551: An Application Control policy has blocked this file` while starting the newly compiled `task7b_host_test.exe`. The preceding `host_test.exe` compiled and ran; the fixture stopped before compiling `interop_host`.

This is an outstanding local execution-policy gate, not a passing firmware result. The earlier 341-test passing run does not override the latest blocked run. No OS policy was changed, no test was skipped to make a green total, and no physical hardware was accessed. The website/backend runtime uses the separately tested Python protocol library and does not execute those firmware host-test binaries.

## Troubleshooting

| Symptom | Action |
|---|---|
| Connection refused | Keep the startup terminal open; inspect its first error. Do not repeatedly open a URL without a running process. |
| Address already in use | Reuse the known service or select a free port. The launcher will not kill an unrelated process. |
| Native `cbor2` import blocked | Use an approved supported runtime or the explicit prepared pure-Python path described above. Do not weaken OS policy. |
| Compiled frontend missing | Build with the existing build script; the launcher will not serve a fabricated replacement page. |
| Configuration not simulation/zero cap | Stop and review why it changed. Do not use the demo launcher to enable hardware. |
| Empty real-sensor panel | Expected before device-specific migration and commissioning. See `R2_HARDWARE_HANDOFF.md`. |
| Map WebGL unavailable | The flagship view can present a labelled schematic fallback, not fake geographic detail. |
| Another phone cannot open localhost | Correct: localhost belongs to each device. This launcher is deliberately loopback-only. LAN/HTTPS exposure is a separate reviewed deployment. |
