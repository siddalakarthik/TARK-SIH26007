# R3 software integration verification and handoff

Subsequent milestone, 5 October 2026: see
[R3_REASONING_REPORT.md](R3_REASONING_REPORT.md). Its final backend run passed
489 tests, including the previously OS-blocked R3 firmware host test; frontend
passed 166 tests. The historical results below are not rewritten or hidden.

Date: 4 October 2026 (Asia/Kolkata). This report covers the current working tree,
not a new commit or deployment. No physical hardware was accessed. No security
policy was changed. No credentials, package upgrades or paid services were added.

## Result

The existing application runs with the additive R3 evidence integration. Evidence
contracts, qualification, clock/calibration/configuration registries, normalized
adapters/fixtures, observation protocol extension, recording/recomputation,
experiments and controlled HMI additions are implemented.

**This is not a full R3 operational software freeze.** Selected device/platform
bindings, the R3 perception/advisory bridge, released model/media reconstruction
and target instrumentation still require work. See Outputs N–P in
[the integration report](R3_SOFTWARE_INTEGRATION.md). Do not reclassify all of
those software tasks as hardware-only verification.

Traction remains `DISABLED_PHASE_1`. The R3 profile does not submit motor commands.
The browser remains monitoring-only with local experiment/recording metadata
controls; those writes are disabled in a public-demo deployment.

## Test history — do not conflate separate runs

| Run | Result | Interpretation |
|---|---|---|
| Baseline before R3 work | 322 passed; 31 setup errors | `task7b_host_test.exe` blocked by Windows Application Control, WinError 4551 |
| Intermediate full R3 run | 418 passed; 0 errors/failures/skips; 62.601 s | The old host executables and new R3 executable actually ran under normal execution; no policy bypass |
| Final full backend run, after source-expiry fix | **419 passed; 1 failed; 0 skipped; 66.40 s** | One failure is Windows execution denial, not an assertion failure; details below |
| Focused R3 runtime tests | **17 passed** | Includes expiry between publication ticks, clock deadline, immutable checkpoint, callbacks/lifecycle, API experiments and replay |
| Final frontend suite | **153 passed; 0 failed** | Includes existing 143 tests and 10 R3 tests |
| TypeScript | **PASS** | `npm run lint:types` |
| Production frontend | **PASS** | `npm run build`; 61 transformed modules |
| Git whitespace/diff check | **PASS** | No whitespace errors; existing unrelated changes retained |

The final denied test is:

```text
backend/tests/test_r3_protocol.py::test_r3_firmware_encoder_interoperability
OSError: [WinError 4551] An Application Control policy has blocked this file

Executable:
../work/pytest_r3_closure_341fe2a802b54232a6ab189fb1b67097/
test_r3_firmware_encoder_inter0/r3_observation_host.exe
```

Compilation succeeded; execution was denied. The executable was not relocated,
renamed, recompiled under a different policy path or run through a workaround.
The latest gate is **UNVERIFIED / OS-BLOCKED**, despite the earlier successful
normal execution. The earlier 31 legacy host cases passed in the final run; they
are not hidden skips. Physical USB, MCU interrupts or board watchdog verification
are not implied by any host result. An authorized environment must execute the
remaining host gate before claiming an entirely passing release regression.

Existing warnings: Starlette/httpx and AnyIO deprecation notices. Vite reports
the pre-existing lazy MapLibre chunk above 500 kB (801.82 kB minified). It remains
lazy-loaded; no arbitrary warning suppression or dependency upgrade was made.

## Exact commands

Run from repository root unless noted. The existing local cbor2 pure-Python
dependency overlay was used; nothing was installed in this pass.

```powershell
$env:PYTHONPATH=(Resolve-Path '..\work\tark_demo_python').Path
$env:PYTHONDONTWRITEBYTECODE='1'
Get-ChildItem Env:TARK_* | ForEach-Object {
    Remove-Item -LiteralPath ('Env:' + $_.Name)
}
```

Full backend invocation:

```powershell
$testTmp=Join-Path (Resolve-Path '..\work') ('pytest_r3_closure_'+[guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp $testTmp --tb=line --junitxml=../work/r3_backend_final.xml
```

Focused runtime command:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_r3_runtime.py -q -p no:cacheprovider --tb=short
```

One attempted focused command named a nonexistent `test_runtime_owner.py`;
pytest collected no tests. It was corrected to the actual R3 runtime test file.
The later full run includes the existing runtime-owner/evidence-harness tests.

From `frontend`:

```text
npm test -- --run --reporter=json --outputFile=../../work/r3_frontend_final.json
npm run lint:types
npm run build
```

These use existing dependencies and scripts. No lockfile/package changes.

## Local demo / startup

Current software-only demonstration URL:
`http://127.0.0.1:8013/#/diagnostics`.
Health: `http://127.0.0.1:8013/health`.
Readiness: `http://127.0.0.1:8013/api/v2/r3/readiness`.
Experiment catalog: `http://127.0.0.1:8013/api/v2/r3/experiments`.

Start from a clean task shell using the environment cleanup above, then:

```powershell
$env:TARK_HARDWARE_PROFILE='R3_PI5_ADVISORY'
$env:TARK_R3_FIXTURE_PATH=(Resolve-Path 'data/fixtures/r3_sources_v1.json').Path
$env:TARK_DATABASE_PATH=(Join-Path (Resolve-Path '..\work') 'r3_browser_qa.db')
$env:TARK_ENV='development'
$env:TARK_AUTH_MODE='public_demo'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8013 --no-access-log
```

This is loopback-only development, not public deployment. `auth_mode=public_demo`
allows viewing without a login; **environment=development** permits local
recording/experiment metadata actions. Do not expose this combination publicly.
For public exposure use the existing controlled deployment configuration, whose
public-demo environment blocks mutations. No deployment was performed here.

The untouched `config/phase1.json` selects simulation with zero hard speed cap.
The explicit fixture path is necessary: selecting R3 alone does not invent data.
Omit the R3 variables to use the default legacy profile. Do not treat any of these
settings as hardware enablement. Existing generic demo launchers are preserved.

## Actual browser verification

The computer-use skill guided UI verification through the existing in-app browser.
No second UI test server, MapLibre instance or WebSocket manager was added.

Final-build workflow:

1. Open Diagnostics, create `R3-CLOSURE-20261004` with synthetic-only test metadata.
2. Open Replay, start then stop recording.
3. Load recording `6aeb66d9-043d-479a-82a4-24068f45cd29`.
4. Verify **149 normalized observation ticks over 41.77 seconds**.
5. Visible result: legacy decision **MATCH**, R3 qualification **MATCH**;
   raw inference **NOT RECOMPUTABLE**, with an explicit explanation.
6. Step forward in the isolated replay timeline.
7. Finish the experiment; load catalog; confirm COMPLETE, recording association,
   149 ticks and the stored R3 MATCH result.

An earlier 83-tick run also matched under its original software fingerprint and
remains in the QA database. A stored catalog result describes that historical
verification, not a guarantee of compatibility after future source changes.

No warnings or errors were captured in the final browser console check. Health
returned ready / simulation / DISABLED_PHASE_1 / NOT_CONNECTED_PHASE_2. Physical
device panels remained unverified; the eight active R3 sources say SIMULATION /
SYNTHETIC_FIXTURE, not REAL. No permission was requested for camera or location.

Final Diagnostics overflow checks, with the experiment catalog visible:

| Viewport width | Document scroll width | Horizontal overflow |
|---:|---:|---|
| 320 | 305 | No |
| 375 | 360 | No |
| 430 | 415 | No |
| 768 | 768 | No |
| 1024 | 1009 | No |
| 1440 | 1425 | No |
| 1920 | 1905 | No |

Temporary viewport overrides were reset. Earlier visual inspections at 375 and
1440 pixels found readable readiness cards without overlaps. These are checks
of the modified views, not a claim of exhaustive usability or physical-display
validation. The existing map architecture was not changed.

Artifacts outside the repo, in `../work`:

- `r3_backend_baseline.xml`: baseline with the 31 denied cases.
- `r3_backend_final.xml`: final 420 collected tests, one OS-blocked failure.
- `r3_frontend_final.json`: 153-test frontend result.
- `r3_responsive_final.json`: final width measurements.
- `r3_replay_verified.jpg`: actual final-build replay screen.
- `r3_browser_qa.db`: synthetic local QA experiment/recording database, not a
  production or physical-hardware recording.
- `r3_http_probe.json`: bounded read-only HTTP measurements.

## Performance evidence — limited and explicit

```text
python scripts/r3_acceptance_probe.py --url http://127.0.0.1:8013 --samples 8 --interval 0.1
```

Final Windows-local run: 8 successes, 0 failures; 189,072 response bytes;
HTTP p50 32 ms, p95 125 ms. This tiny sample is a smoke measurement, not a service
SLA or Pi 5 real-time result. CPU/temperature/throttling remain unavailable.
Inference supports bounded latency samples, p50/p95, FPS and dropped busy frames;
no real model or accelerator was run. Full target benchmarking remains open.

## Defects corrected during integration

- Retained-history eviction no longer increments transport packet loss.
- Readiness and recorded evidence are captured atomically against callbacks.
- Unknown/failed health, wrong identity/mode and missing calibration cannot
  become qualified merely because a device is connected.
- Explicit peer position uncertainty and optional correction requirement prevent
  “good fix” labels from automatically qualifying cooperative position.
- Changed on-disk R3 code requires a runtime restart before a new recording.
- Cached publication respects source-age and clock-mapping expiry without
  altering the decision or its persisted checkpoint.
- Completed experiment results are now accessible in a bounded read-only HMI
  catalog, rather than only the API.

## Files in this R3 change set

New:

```text
backend/app/r3/__init__.py
backend/app/r3/adapters.py
backend/app/r3/contracts.py
backend/app/r3/cooperative.py
backend/app/r3/evidence.py
backend/app/r3/experiments.py
backend/app/r3/inference.py
backend/app/r3/registry.py
backend/app/r3/replay.py
backend/app/r3/runtime.py
backend/app/r3/sources.py
backend/app/r3/vendor.py
backend/tests/test_r3_evidence.py
backend/tests/test_r3_protocol.py
backend/tests/test_r3_runtime.py
config/r3_pi5_advisory.json
data/fixtures/r3_sources_v1.json
r3_protocol_vectors.json
firmware/esp32/tests/r3_observation_host.c
firmware/esp32/tests/r3_protocol_vectors.h
frontend/src/features/r3/contract.ts
frontend/src/features/r3/R3Evidence.tsx
frontend/src/features/r3/R3Evidence.test.tsx
frontend/src/features/r3/r3.css
scripts/r3_acceptance_probe.py
docs/R3_SOFTWARE_INTEGRATION.md
docs/R3_VENDOR_FORMATS.md
docs/R3_ESP32_OBSERVATION_PROTOCOL.md
docs/R3_VERIFICATION_REPORT.md
```

Modified existing files (some already contained uncommitted R2 work):

```text
.env.example
backend/app/main.py
backend/app/services/system.py
backend/app/services/runtime.py
backend/app/communication/esp32/protocol.py
backend/app/flagship.py                 (R3 description strings only)
firmware/esp32/main/protocol/tark_protocol.c
firmware/esp32/main/protocol/tark_protocol.h
firmware/esp32/main/protocol/response.c
firmware/esp32/main/protocol/response.h
firmware/esp32/main/protocol/service.c
firmware/esp32/main/protocol/service.h
frontend/src/types.ts
frontend/src/api.ts                    (replay result type extension)
frontend/src/app/FlagshipApp.tsx
frontend/src/features/replay/ReplayPanel.tsx
scripts/generate_protocol_vectors.py
```

Other dirty R2 frontend/tests/docs/scripts/studies in `git status` predate this
integration. They were not reset or attributed to this pass. No commit/push was
made. No safety/PV-SOE/TTC math, motor driver, E-stop, watchdog or MapLibre logic
was modified in this R3 pass.

## Honest release conclusion

**Evidence integration foundation: implemented and exercised.**
**Final whole-R3 operational freeze: NOT READY.**

Remaining software: selected real transport/runtime bindings; R3 perception and
advisory semantic bridge; model/media reconstruction; PPS/UTC producer and target
resource/throughput instrumentation. Remaining execution gate: the one denied
R3 C-host executable. Remaining physical work: equipment identity, wiring,
clock/calibration measurements, network/storage/power and field evaluation.

No purchased R3 device, MCU flash, physical encoder, camera, radar, GNSS, E-stop,
motor or mine operation has been verified by this work.
