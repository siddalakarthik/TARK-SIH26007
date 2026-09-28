# Phase 1 software integrity correction

> SCOPED CORRECTION EVIDENCE — historical run counts and forward-looking
> statements below describe this correction stage. Its source/evidence remains
> applicable as recorded; [R1](TARK_RELEASE_MANIFEST.md) controls current identity,
> combined counts and remaining scope. [Protocol V2](ESP32_PROTOCOL_V2.md) is current.

## A. Baseline

- Starting branch: `main`; HEAD `430a9f78fe69ee6870eb2cd9004600880a2dc028`.
- Starting working tree: clean; no unrelated user changes.
- Correction branch: `tark/software-integrity-correction`.
- Existing tag `tark-software-freeze-2026-09-20` is unchanged.
- Versions: Python package 0.1.0; FastAPI/HMI diagnostics 0.3.0; frontend package 0.2.0; Protocol V1.
- Configuration: `config/phase1.json`, simulation, `UNRELEASED-PHASE1`, hard cap 0.0 m/s.
- No physical hardware access. Tests use isolated databases, fake clocks and mocked devices.

## B. Reproduction table (captured BEFORE production source changes)

| ID | Reported defect | Current source path | Executable reproduction | Observed before-fix result | Reproduced | Severity | Planned correction |
|---|---|---|---|---|---|---|---|
| SI-01 | Stale queued evidence supports current NORMAL | backend/app/services/{system,pipeline}.py | test_si01_queued_old_report_cannot_publish_normal; report 1 s, final time 10 s | NORMAL, expected UNKNOWN | YES | High, critical before traction | Preserve observation time; decide once at final runtime time |
| SI-02 | Future observation classified fresh | backend/app/services/pipeline.py | test_si02_future_cannot_be_fresh; now + 1 ns | FRESH | YES | High | Strict invalid timestamp rejection, no invented tolerance |
| SI-03 | Consumers advance execution | backend/app/main.py | test_si03_rest_reads_do_not_advance_decisions; four GETs | sequence 0 -> 4 | YES | High | One lifespan-owned scheduler; readers consume snapshots |
| SI-04 | Zero deceleration passes validation | backend/app/config.py | test_si04_zero_deceleration_rejected | No ValidationError | YES | High | Finite parameters; deceleration strictly positive |
| SI-05 | Unavailable measured speed displayed as zero | frontend/src/features/dashboard/DriverView.tsx | DriverView.integrity.test.tsx rendered DOM | Current speed / 0.00 m/s | YES | Medium | Measured speed UNAVAILABLE, command speed separate |
| SI-06 | TTC absence hidden behind N/A | frontend/src/features/dashboard/DriverView.tsx | DriverView.integrity.test.tsx rendered DOM | TTC / N/A | YES | Medium | NOT COMPUTED, no TTC integration |
| SI-07 | State-named scenarios silently alias default | backend/app/hardware/simulators.py | test_si07_state_names_are_not_silent_aliases and direct scenario execution | WARN accepted; NORMAL/WARN/RESTRICT/UNKNOWN/STOP all yield NORMAL | YES | High | Retain descriptive input scenarios; reject undefined state aliases |
| SI-08 | Stale UI/marker/heading look current | frontend/src/{app/OperationsApp,MapView}.tsx | OperationsApp reconnect test; MapView.lifecycle.test.tsx | Snapshot retained; marker/accuracy/trail not cleared; unknown heading is north arrow | YES | High | Clear invalid telemetry/location; neutral unknown-heading symbol |
| SI-09 | Public recording mutation permitted | backend/app/main.py | test_si09_public_recording_mutation_rejected | Public POST start returns 200 | YES | High | Server-side public-environment mutation prohibition |

Initial executable results: backend integrity 6 failed (one per backend issue); frontend driver/reconnect 3 failed with 25 existing tests passed; MapView lifecycle 4 failed. These are expected red regressions, not a claim that baseline production was corrected.

## C. Defects not reproduced

None of SI-01 through SI-09 was disproven. Detailed coverage is being extended; no physical claim is made.

## D. Root causes and controlled choices

- Ingestion restamps observations; queued reports are evaluated at their old time, not final decision time.
- Future ages are negative and satisfy the fresh comparison. No approved tolerance was found: use strict rejection of future/negative/invalid observation times.
- REST and WebSocket handlers own tick calls; no independent owner exists.
- Generic nonnegative configuration permits zero deceleration and infinity.
- Speed/TTC UI uses literal zero/N/A rather than availability semantics.
- Scenario names lack an executable state-transition contract. WARN SEMANTICS NOT YET DEFINED IN PRODUCTION CONTRACT. No new WARN or TTC policy will be invented.
- Reconnect does not invalidate cached telemetry; map effect returns before clearing disappeared location.
- Public UI hides mutation controls, but server dependencies permit mutation.

### Scenario evidence and retained meaning

With the reviewed phase1.json, a new pipeline and time 1 s:

| Old input name | Input condition | Before result | Planned retained meaning |
|---|---|---|---|
| NORMAL / WARN / RESTRICT / UNKNOWN | same target (3, 0.25 m), velocity -1 m/s | NORMAL | Reject these unsupported state aliases; use TARGET_APPROACH |
| STOP | same target, velocity -3 m/s | NORMAL | Rename FAST_TARGET_APPROACH; it does not promise STOP |
| TARGET_APPROACH | target, velocity -1 m/s | NORMAL | Retain |
| TARGET_RECEDING | target, velocity +1 m/s | NORMAL | Retain; no TTC policy added |
| MULTI_TARGET | two targets, nearest at (3, 0.25 m) | NORMAL | Retain |
| RADAR_LOSS / RADAR_STALE | no report | UNKNOWN from empty pipeline | Retain; after prior input state follows freshness, not name |

Configuration identity: `AUTO` retains the existing raw-file SHA-256 calculation. A manually supplied value is an identifier, not cryptographic/release verification. No release-management migration is included.

## E. Implementation and files changed

All SI-01 through SI-09 were reproduced and corrected within this pass.

- SI-01/02: `Pipeline.observe()` separates evidence ingestion from decisions. Report and detection timestamps are preserved; out-of-order reports cannot overwrite newer evidence. Negative/future/invalid timestamps reject the report and expose FAILED/STALE health with INVALID_OBSERVATION_TIMESTAMP. Each tick evaluates once at its controlled current time. A stale track cannot borrow freshness from a newer report. No clock tolerance was invented.
- Existing boundaries are retained: age <= fresh is FRESH; fresh < age <= stale is AGING; age > stale is STALE. Existing AGING decision behavior is retained, not replaced with a new WARN policy. Integer nanosecond comparisons cover one-unit boundaries.
- A NORMAL decision carries its supporting evidence deadline. A publication read after that deadline returns unavailable rather than extending the decision's validity. Reads do not recompute decisions or generate events.
- SI-03: one FastAPI-lifespan RuntimeOwner starts with one initial tick, then waits 250 ms after each completed step. No catch-up bursts. The existing single-worker run/Docker commands are retained; multiple application workers against one vehicle are not supported. GET status/tracks/sensors/location and WebSocket publication read detached snapshots. GET events only reads persistence. No observer can advance the command sequence, event count or GNSS simulator.
- Runtime shutdown cancels/awaits its task before closing resources. Duplicate startup is rejected without canceling the existing owner. Sequential application restarts construct fresh resources. Unstarted, stopped, failed or expired snapshots are unavailable; status/readiness return 503 and WebSocket closes with 1013. Worker failures are not suppressed at shutdown. `/health` remains a liveness response with truthful ready/unavailable status; `/ready` is the deployment readiness gate.
- SI-04: finite nonnegative numeric parameters; deceleration strictly positive; zero remains valid for margin, reaction bound and hard cap. Configuration identifiers remain unchanged.
- SI-05/06: measured speed UNAVAILABLE, TTC NOT COMPUTED, separately labelled commanded permitted speed and DISABLED_PHASE_1. The API adds timestamp, NORMAL-evidence validity deadline and measurement availability labels; existing fields remain compatible. No measured speed or TTC value was invented.
- SI-07: descriptive scenario inputs retained; the former STOP input is FAST_TARGET_APPROACH. Undefined state-named aliases fail explicitly. No state is injected and no WARN threshold is introduced.
- SI-08: reconnect/offline/degraded telemetry clears current values and vehicle location. Late REST results and retired socket callbacks cannot restore them. Missing/stale location removes the vehicle marker, accuracy and trail; known coordinates shown alongside stale status are labelled LAST KNOWN. Unknown heading uses a neutral dot, not a north arrow. Invalid location messages clear vehicle-location evidence.
- SI-09: public_demo environment recording POSTs return 403 server-side. Local development and authenticated operator workflows retain authorization. Replay verification and route/reverse queries are non-persistent computations, not recording mutations; no new authentication platform was added.

Exact intended file set:

```text
backend/app/config.py
backend/app/domain/models.py
backend/app/hardware/simulators.py
backend/app/main.py
backend/app/services/pipeline.py
backend/app/services/runtime.py (new)
backend/app/services/system.py
backend/tests/runtime_fixtures.py (new)
backend/tests/test_api.py
backend/tests/test_location_camera.py
backend/tests/test_software_integrity.py (new)
backend/tests/test_startup_contract.py
frontend/src/MapView.tsx
frontend/src/MapView.lifecycle.test.tsx (new)
frontend/src/api.ts
frontend/src/api.test.ts
frontend/src/app/OperationsApp.tsx
frontend/src/app/OperationsApp.test.tsx
frontend/src/features/dashboard/DriverView.tsx
frontend/src/features/dashboard/DriverView.integrity.test.tsx (new)
docs/SIMULATION.md
docs/FAULT_MATRIX.md
docs/SOFTWARE_INTEGRITY_CORRECTION_REPORT.md (new)
```

## F. Tests added / compatibility changes

65 backend integrity cases and 14 additional frontend cases cover the reproduced defects, timestamp/numeric boundaries, observer independence, shutdown/restart, failed workers, cache expiry, source labels, public authorization, reconnect races and map lifecycle.

Existing tests were retained. API/startup/location tests that previously omitted the FastAPI lifespan now enter it. Recording tests now advance an injected runtime clock instead of incorrectly expecting a GET to generate a recording. The exact record-count and replay assertions remain. The invalid-location frontend test now expects evidence clearing, rather than silent retention of the prior valid fix. No test was deleted or skipped to obtain a green full suite.

## G. Full regression results

| Executed check | Result |
|---|---|
| Complete backend pytest suite | 162 passed; two existing dependency deprecation warnings |
| Complete frontend `pnpm test` | 39 passed, 9 files |
| `pnpm run lint:types` | PASS |
| `pnpm run build` | PASS; existing >500 kB lazy MapView chunk advisory remains |
| Focused backend integrity suite, re-run after review | 65 passed |
| Targeted frontend post-fix red-team selection | 7 passed; 17 intentionally not selected by `-t "red team"`; these pass in the full suite |

Backend execution used the available bundled Python with the existing project site-packages (no installation). Before importing app modules the test process removed inherited TARK_* variables and set TARK_DATABASE_PATH=:memory:. Tests that need disk persistence use pytest temporary directories; hardware lifecycle tests use existing injected fakes.

Exact backend runner shape (from repository root):

```python
import os, sys
for key in tuple(os.environ):
    if key.startswith("TARK_"): del os.environ[key]
os.environ["TARK_DATABASE_PATH"] = ":memory:"
sys.path.append(".venv/Lib/site-packages")
import pytest
raise SystemExit(pytest.main(["-q", "-p", "no:cacheprovider"]))
```

The script was piped to the bundled Python with `-B -`; the focused run adds `backend/tests/test_software_integrity.py`. Standard installed-environment equivalent: `python -B -m pytest -q -p no:cacheprovider` with the same isolated environment.

Frontend targeted command: `node node_modules/vitest/vitest.mjs run --environment jsdom src/api.test.ts src/app/OperationsApp.test.tsx src/MapView.lifecycle.test.tsx -t "red team"`. The available pnpm shim did not support `pnpm exec vitest`; the existing package scripts and direct local Vitest entry were used without dependency changes.

## H. Post-fix adversarial results

| Attack | Observed corrected result |
|---|---|
| Nine-second-old queued report | UNKNOWN at final decision time; original track time retained |
| Fresh report carrying an expired detection | Cannot support NORMAL |
| NOW+1 ns and far-future timestamps | Rejected; UNKNOWN, no capability increase |
| Exactly fresh/stale boundaries and one ns beyond | Preserved inclusive boundaries; one ns past stale -> UNKNOWN |
| Cached NORMAL crosses evidence deadline between ticks | Publication 503, no observer-created decision |
| No observers / one REST / repeated REST / one WS / three WS / repeated reconnect | Same logical trace: (2,NORMAL), (3,UNKNOWN), (4,UNKNOWN); identical tick/event/sequence count |
| Repeated REST reads including vehicle location | No additional ticks, commands, events or simulated location steps |
| Queued batch | One final decision/event/command, not one per queued report |
| Runtime restart / duplicate startup / fixture storage failure | Clean lifecycle; duplicate rejected; failure unavailable and propagated |
| Zero deceleration / NaN / +/-Infinity / negative parameters | Configuration validation fails before runtime |
| Reconnect / offline / degraded / delayed REST / retired socket callbacks | No stale current-looking NORMAL restored |
| Eight socket reconnect cycles | One retry timer; retired callbacks ignored; shutdown clears timers |
| Missing/stale map fix / eight disappear-recover cycles | Current marker/accuracy/trail cleared; one map instance retained within the mounted component |
| Unknown heading | Neutral marker, not a confirmed north arrow |
| Public recording POST | 403, no session mutation; intended non-public authorization still works |

All exercised command paths retained zero permitted speed and zero left/right commands. These are software-only regression results, not physical safety verification.

## I–J. Known remaining work / deferred Prompt 2

Replay empty-report/batch/initial-state semantics and full-session verification are deferred explicitly to Prompt 2. The existing recording format was not redesigned; no claim of complete replay correctness is made.

Previously audited protocol clock/CBOR/ACK/firmware-lifecycle defects remain outside this pass. The audited sensor identity/bootstrap/I2C-bus limitations, GNSS UTC aggregation and event timestamp/retention issues likewise remain; this task did not attempt to close the full audit. No newly discovered out-of-scope safety defect was used as a reason to expand implementation.

No EKF, fusion, TTC/WARN policy, physical control or electrical work was implemented. The simplified PV-SOE model and zero-speed decision assumption remain explicitly provisional. Historical whole-system freeze claims are not reaffirmed. Prompt 1 is ready for the separately scoped Prompt 2, not for traction or a blanket project freeze.

## K. Safety invariants

Required throughout: traction == DISABLED_PHASE_1; permitted_speed_mps == 0.0; left_command == 0; right_command == 0. No browser motion authority, hardware access, tag rewrite or push.

Confirmed in focused and full regression runs. No COM/USB/I2C device, camera, motor or contactor was opened/operated. No firmware/electrical/dependency/deployment configuration file was changed. Generated frontend build output, caches, databases and test artifacts remain ignored and are not part of the intended commit.

Final intended-files audit passed: exactly the 23 files listed above. `git diff --check` and staged whitespace checks passed; full backend/frontend/type/build gates were repeated successfully after code review. Existing freeze tag was not moved. One local correction commit is authorized; no push is authorized or performed.
