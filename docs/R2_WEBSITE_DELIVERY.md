# TARK R2 website — delivery and verification

3 October 2026 · Local, software-only demonstration · Not a hardware or safety release

## Open the application

- Main workspace: `http://localhost:8000/`
- Driver view: `http://localhost:8000/#/hmi`
- Map: `http://localhost:8000/#/map`
- Readiness: `http://localhost:8000/health`

FastAPI serves the compiled React application and its REST/WebSocket endpoints from one origin. A viewer needs only a browser. The local server must remain running; localhost is not a public URL or an address another phone can use.

On this prepared workstation, run from the repository in PowerShell 7:

```powershell
.\scripts\run_demo.ps1 -DemoPythonPath '..\work\tark_demo_python'
```

See [R2_WEBSITE_RUN.md](R2_WEBSITE_RUN.md) for normal installations, build commands, the optional official pure-Python CBOR dependency, Linux preparation and troubleshooting. The legacy Windows PowerShell installation on this workstation rejected script execution; no execution policy was changed. The already available PowerShell 7 environment runs the launcher.

## Delivered website

| Area | Working behavior |
|---|---|
| Shared application | One responsive shell with Overview, Map, Sensors, Safety, Events, Replay, Diagnostics and Settings; driver, control-room and owner views; persistent night/day preference; keyboard skip link and focus indicators. |
| Driver | Large plain-language action and reason, explicit research state, unavailable measured speed and uncomputed TTC shown honestly. No steering, motor, brake or physical E-stop control. |
| Control room | Existing decision values, local radar, current sources, bounded recent events and independent fleet demonstration. |
| Owner | Existing research state and actual observation-window record count. No invented haul-cycle, downtime, incident or fleet-productivity metrics. |
| Offline map | One MapLibre instance with a synthetic course, two participants, route, restricted zone, inert hazard, breadcrumbs, uncertainty circles, participant selection, follow, compass, zoom, fit and scale. A labelled SVG fallback is retained for unavailable WebGL. |
| Geographic map | Existing free, key-free OpenFreeMap layer remains available separately. Provider failure leaves the local website and decision path running. Browser-device location remains distinct and is not automatically requested. |
| Radar | Full local X/Y plane, including rear targets; finite observations only, at most 50 displayed targets, and an explicit omission count. No geographic placement of local radar. |
| Sensors | Sequential, cancellable camera-status polling, metadata validation, timeout and stale-frame removal. No automatic browser-camera access. New BOM readiness is distinguished from retained legacy drivers. |
| Events | Up to 100 recent records, deduplication, search, severity/type filtering and selected-record evidence. Monotonic source time is not labelled as wall-clock UTC. |
| Replay | Existing persisted recording catalog, load, play/pause, step, reset, seek and recomputation verification. Replay stays separate from current observations. |
| Data integrity | Complete snapshot field validation, finite values, bounded arrays/text and known safety states. Fleet age advances locally, duplicate observations cannot refresh it, and out-of-order or invalid frames are rejected. |
| Connection loss | Current-looking decision and fleet values are removed when the observation connection degrades or disconnects. Reconnection restores newly received observations. |

The flagship course is deliberately a **separate presentation fixture**. It does not supply radar detections or participate in PV-SOE. Showing a moving node beside the decision panel is not a claim that cooperative collision avoidance has been implemented. Node B is location-only, not a second full sensor vehicle. A course while moving is not claimed as body heading when stationary.

## Verification results

### Automated checks

- Frontend: **143 passed**, 13 test files, no failures.
- TypeScript: `npm run lint:types` passed.
- Production build: `npm run build` passed. The existing MapLibre chunk is approximately 802 kB minified / 218 kB gzip and produces Vite's large-chunk warning. The map is lazy-loaded; the warning was not suppressed.
- Full backend: **322 passed, 31 setup errors**, 353 collected; three deprecation warnings. All 31 errors share the firmware host-test fixture: Windows Application Control blocked `task7b_host_test.exe` with **WinError 4551**. The preceding `host_test.exe` ran. This is not a passing firmware interoperability result; no OS security policy was changed.
- Shell launcher: syntax passed and **7 mocked checks under Python `-O` passed**. Incompatible mode/cap and invalid ports fail closed even with assertions disabled.
- `git diff --check`: passed. No commit or push was performed.

Frontend commands were run in `frontend` using installed dependencies, without upgrades:

```text
npm run lint:types
npm test
npm run build
```

### Real-browser checks

Chromium was run against the actual local FastAPI application, not an HTML mock-up:

- All eight navigation sections loaded without an application exception.
- All eight sections checked at **320, 375, 430, 768, 1024, 1440 and 1920 px**: no horizontal page overflow.
- Map canvas retained nonzero height; mobile participant markers remained inside its bounds and controls did not overlap.
- Repeated map/overview navigation retained one active map canvas; WebGL2 worked in both default headless and the existing software-rendering test profile.
- Participant selection and Follow A worked.
- Event search, filter clearing and selected evidence worked.
- A real local **simulation recording** was created, stopped, loaded, stepped, reset, played, paused and verified: **MATCH**. QA recordings remain in the separate local `r2_demo.db`; no user recording was deleted or replaced.
- Day/night preference survived a reload; all three role views worked.
- A deliberate browser-network outage removed current-looking values; restoring connectivity recovered the display. The expected `ERR_INTERNET_DISCONNECTED` messages during that deliberate outage were not application exceptions.
- The default offline course made no external requests and produced no console errors during normal checks.
- Geographic OpenFreeMap loading succeeded with `MAP AVAILABLE`, proper attribution and no console/network failures after network permission was available. It also displayed a truthful offline state during a denied-network check. No browser geolocation or physical camera permission was requested.

Evidence and repeatable workstation QA scripts are in the workspace's `work/` directory, outside application source: `qa_tark_r2.mjs`, `qa_tark_r2_functional.mjs`, `qa_tark_r2_geographic.mjs`, `diagnose_flagship_map.mjs` and `qa_tark_r2_performance.mjs`. Screenshots and JSON reports are under `work/tark_r2_browser_qa/` and `work/flagship_map_diagnostics/`. These scripts name the installed workstation browser; they are not portable deployment prerequisites.

### Small performance sample — not a production benchmark

One 1440×1000 headless-browser run on this development PC measured:

- First connected overview with participant marker: **872 ms**.
- One observation WebSocket and one map canvas.
- JavaScript heap: approximately **18.0 MiB**.
- Browser main-thread task time: approximately **12% of a five-second sample**. This is not system CPU utilization.
- Five fleet polls over that sample, with no overlapping poll requests.
- Twenty sequential local flagship requests: median **9.1 ms**, sample p95 **21.3 ms**, maximum **342.5 ms**. The outlier is retained rather than hidden.

These measurements do not establish Raspberry Pi inference capacity, fleet scalability, network safety latency or physical sensor performance.

## Files changed by the website work

New implementation:

- `backend/app/flagship.py`, `backend/tests/test_flagship.py`
- `frontend/src/app/FlagshipApp.tsx`
- `frontend/src/features/flagship/{FlagshipDashboard.tsx,FlagshipDashboard.test.tsx,FlagshipMap.tsx,FlagshipMap.test.tsx,Icons.tsx,types.ts,useFlagship.ts,useFlagship.test.tsx,flagship-map.css}`
- `frontend/src/features/events/EventTimeline.test.tsx`
- `frontend/src/operations.css`, `frontend/public/tark-mark.svg`
- `scripts/run_demo.ps1`, `scripts/run_demo.sh`
- `docs/R2_WEBSITE_RUN.md`, `docs/R2_HARDWARE_HANDOFF.md`, this report

Existing files adjusted:

- `backend/app/main.py`: authenticated read-only flagship endpoint and no-store response only.
- `frontend/index.html`, `frontend/src/main.tsx`: application metadata and stylesheet entry.
- `frontend/src/app/OperationsApp.tsx`, `OperationsApp.test.tsx`: new shell entry and navigation/integrity regressions.
- `frontend/src/api.ts`, `api.test.ts`: existing snapshot validator and optional cancellable camera-status request.
- `frontend/src/features/dashboard/DriverView.tsx`, `DriverView.integrity.test.tsx`.
- `frontend/src/features/events/EventTimeline.tsx`.
- `frontend/src/features/owner/OwnerView.tsx`.
- `frontend/src/features/sensors/CameraPanels.tsx`, `CameraPanels.test.tsx`.

Other pre-existing untracked research documents and studies were preserved. Application dependencies, lockfiles, Docker/Render configuration, core decisions, perception, GNSS drivers, ESP32 protocol/firmware and motor authority were not changed by this website pass.

## What is not complete

This is a working **website demonstration**, not a declaration that the new hardware platform is plug-and-play or safety validated.

1. Newly selected TI radar, BNO085, Lepton/PureThermal, GNSS peer/correction paths and the new compute/AI setup still require their specific software integration and recorded-fixture tests where listed in [R2_HARDWARE_HANDOFF.md](R2_HARDWARE_HANDOFF.md). Old LD2450/BNO055/MLX90640 drivers are not silently reused as verified replacements.
2. The flagship API intentionally returns unavailable participants outside simulation until the real normalized multi-node publication path exists. The older normalized vehicle-location service remains separate and preserved.
3. All physical identity, wiring, calibration, time alignment, sensor performance and site validation remain pending. No COM, USB, I2C, motor or E-stop tests were performed.
4. A surveyed mine map, approved route, external address/routing provider and actual fleet operational metrics are not supplied by a free basemap. Unavailable functions remain labelled unavailable.
5. The compiled firmware host-test policy gate is unresolved; the full software stack is not newly declared frozen by this UI pass.
6. This launcher is loopback-only. Public HTTPS/LAN deployment and Raspberry Pi performance acceptance are separate steps. No fabricated public URL is provided.

Traction remains `DISABLED_PHASE_1`. The browser remains monitoring-only. The selected human-operated cart is not turned into an autonomous or browser-driven vehicle by this website.
