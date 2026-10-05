# TARK R3 — SIH pre-selection software freeze

5 October 2026 · **Software simulation/evidence baseline, not hardware release**

## A. Baseline identity

Starting commit: `d385b055bef23af3b01960f7b2c113c2e683fe59`.
Branch: `tark/sih26007-requirement-simulations`.
Previously completed, uncommitted R2 UI/R3 integration, protocol, reasoning,
tests and design/study documents were preserved. This freeze checkpoints that
actual accumulated work together with the three SIH demos; it does not invent
earlier commits or claim every file was created by this final pass.

Current R3 software fingerprint:
`5c7ff4dd69ed647ae15deed580a2e70631669d1da17091d903ca17d9a99aff76`.
The fingerprint covers normalized contents of the existing R3 Python modules.
It is not the Git commit hash or a fingerprint of the entire repository.

Authority: [R3 reasoning report](R3_REASONING_REPORT.md),
[design review](R3_REASONING_DESIGN_REVIEW.md), [vendor boundaries](R3_VENDOR_FORMATS.md),
[protocol](R3_ESP32_OBSERVATION_PROTOCOL.md). Earlier foundation reports are
milestones, not current totals. R1 and R2 history is retained and indexed.

## B–D. Three demonstrations and commands

| Demo | Persisted ticks | Stage endpoints | Qualification / R3 replay |
|---|---:|---|---|
| DEGRADED-VISIBILITY | 45 | NORMAL → RESTRICT → UNKNOWN → sustained NORMAL | MATCH / MATCH |
| COLLISION-RISK | 42 | NORMAL baseline → UNKNOWN entry → RESTRICT → RESTRICT → STOP | MATCH / MATCH |
| BLIND-CURVE | 30 | NORMAL → RESTRICT conflict → UNKNOWN after peer expiry | MATCH / MATCH |

Exactly three sequences use production admission, qualification, reasoner,
Why, existing SQLite RecordingStore and isolated recomputation. Recordings are
closed/reopened before comparisons. The fixture channel/checkpoint is unchanged
by replay. No live channel publication or transport occurs.

Run from the existing installed project Python environment:

```text
python -B scripts/run_sih_demos.py --scenario all --output ../work/sih_preselection
python -B scripts/run_sih_demos.py --scenario degraded-visibility --output ../work/sih_run_2
python -B scripts/run_sih_demos.py --scenario collision-risk --output ../work/sih_run_3
python -B scripts/run_sih_demos.py --scenario blind-curve --output ../work/sih_run_4
```

Choose fresh output directories. Each demo exports metadata, full records,
per-tick summary, the SQLite session and a static `presentation.svg` card.
Detailed expectations and 30–45-second narration:
[SIH_FLAGSHIP_DEMOS.md](SIH_FLAGSHIP_DEMOS.md).

Local dashboard, after the pinned frontend build:

```powershell
$env:TARK_HARDWARE_PROFILE='R3_PI5_ADVISORY'
$env:TARK_R3_FIXTURE_PATH=(Resolve-Path 'data\fixtures\r3_sources_v1.json').Path
.\scripts\run_demo.ps1 -Port 8014
```

Open `http://127.0.0.1:8014/#/safety`; `/#/hmi` is Driver,
`/#/diagnostics` is evidence readiness, `/#/replay` is the existing replay UI.
This uncommissioned runtime fixture remains UNKNOWN where calibration/coverage
is absent. It is **not** the three positive-envelope CLI sequences. No new UI,
WebSocket, live decision loop, dependency, cloud feature or control path was added.
For normal setup and the optional workstation CBOR overlay, see
[R2_WEBSITE_RUN.md](R2_WEBSITE_RUN.md).

## E–F. Verification — final current source

- Focused demo tests: **8 passed**; the same eight pass in the final full run.
- Full backend: **497 passed, 0 failed, 0 skipped**, 105.51 s, two existing
  dependency deprecation warnings. This includes fresh strict GCC compilation
  and execution of the protocol and R3 observation host fixtures.
- Frontend: **166 passed across 15 files**.
- TypeScript `lint:types`: PASS. Production build: PASS.
- Existing controlled scenario matrix: **25/25 passed**.
- Existing 300-tick normalized qualification + advisory replay: **MATCH / MATCH**.
- Three flagship recordings: all persisted ticks compared, **MATCH / MATCH**;
  replay/live isolation verified. Original evidence remains SIMULATION;
  comparisons are REPLAY. Raw image/model inference remains NOT RECOMPUTABLE.
- Existing Safety, Diagnostics, Replay and Driver screens checked at **1440 px
  and 375 px**: simulation/disabled-traction labels, nonzero content, no document
  horizontal overflow, no captured warning/error console entries. No UI source
  changes were necessary in this final pass. The browser did not allow local
  file-protocol SVG preview; no policy workaround was attempted.
- Git whitespace/diff validation passed after trimming five historical design
  documents' extra EOF blank lines. Scoped `.gitattributes` exempts only archived
  renderer SVG/official HTML trailing whitespace and treats the official PDF as
  binary diff data; those hash-inventoried study files were not rewritten.

Exact test commands (repository root; frontend commands from `frontend`):

```text
python -B -m pytest backend/tests/test_sih_demos.py -q -p no:cacheprovider
python -B -m pytest backend/tests -q -p no:cacheprovider --tb=short --basetemp=<NEW_WORKSPACE_TEMP_DIRECTORY> --junitxml=../work/r3_preselection_backend_final.xml
python -B scripts/r3_reasoning_demo.py --output ../work/r3_preselection_evidence_final --ticks 300
npm test -- --reporter=default --reporter=json --outputFile=../../work/r3_preselection_frontend.json
npm run lint:types
npm run build
git diff --check
git diff --cached --check
```

On this workstation the existing pure-Python CBOR dependency directory was
selected with `$env:PYTHONPATH=(Resolve-Path '..\work\tark_demo_python').Path`
and `$env:PYTHONDONTWRITEBYTECODE='1'`. No dependency was installed/upgraded.
The first full run had **407 passes / 90 setup errors** because pytest could not
access its existing default temp root (WinError 5); no assertion failed. A new,
previously nonexistent workspace `--basetemp` resolved that storage access
problem. No directory permissions or application-control policy was changed;
no old temp files were deleted. Final XML is the authoritative successful run.

Local evidence (not committed): `../work/sih_preselection_final/`,
`../work/r3_preselection_evidence_final/`, `../work/r3_preselection_backend_final.xml`,
`../work/r3_preselection_frontend.json`, `../work/r3_preselection_safety.jpg`.

## G. Git release identity

Existing remote: `https://github.com/siddalakarthik/TARK-SIH26007.git`.
Verified source checkpoint: `7a57c3c81efeac1f76f629fab501a1cd578dcf54`,
`feat: checkpoint R3 integration and SIH flagship demonstrations`.
This contains the previously accumulated R2/R3 work and final demo additions.
The subsequent documentation-only commit is `chore: prepare R3 preselection freeze`.
Annotated release tag: `tark-r3-sih-preselection-v1` (not previously present).
Resolve the exact tagged commit with:

```text
git rev-parse tark-r3-sih-preselection-v1^{commit}
git show --no-patch tark-r3-sih-preselection-v1
```

The checkpoint was committed after the verified staging gate. The final tag
identifies the complete tree including this handoff, without
a circular claim that a document can contain its own final commit hash.
GitHub fetch/push remains blocked as described below; the release is local.

The default Windows Schannel fetch returned SEC_E_NO_CREDENTIALS. Per-command
OpenSSL requests retained certificate verification but Git Credential Manager
exited 1 without supplying credentials. An anonymous, noninteractive read-only
check confirmed: `fatal: could not read Username for 'https://github.com':
terminal prompts disabled`. GitHub CLI is not installed. **Fetch/push blocked
by authentication**; cached upstream equality is not fresh remote verification.
No global Git/security configuration was changed. The verified commit/tag can
be completed locally, but no safe-push or public-deployment claim is made.

Human action: sign in to GitHub through the normal Git Credential Manager flow
when running `git -c http.sslBackend=openssl fetch origin` from the repository.
Never paste credentials into chat. After successful authentication, compare
the branch against its fetched upstream, then use normal push only:

```text
git -c http.sslBackend=openssl fetch origin
git rev-list --left-right --count HEAD...origin/tark/sih26007-requirement-simulations
git -c http.sslBackend=openssl push origin tark/sih26007-requirement-simulations
git -c http.sslBackend=openssl push origin tark-r3-sih-preselection-v1
```

If the fetched upstream contains unknown commits, stop and review before
pushing. Never force-push. These are pending commands, not completed operations.

## H. Conservative cleanup and inventory

KEEP: production backend/frontend/firmware, tests, manifests/lockfiles,
configuration, required fixtures, scripts and current R3 documentation.

HISTORICAL, retained in place: R1 release/evidence; earlier R2 hardware/design
packages; isolated `studies/sih26007_simulation` research bundle. Its published
figures/results/source archive/manifest/hashes form one intentional evidence
package, not temporary browser QA clutter. Do not confuse its independent model
with the three production-path demos. Entry-point supersession notices and the
release index clarify which material is current; no historical results are rewritten.
All 103 entries in the retained study's existing hash inventory matched local
files after cleanup; archived evidence bytes were not altered.

IGNORE, retained locally: `.env`, virtual environments, node_modules, build
outputs, caches, databases/logs/recordings, workspace QA evidence, coverage/temp
outputs and OS metadata. New ignore rules do not hide source or config fixtures.
No ambiguous file was deleted, no destructive cleanup or history rewrite used.
Earlier absolute temp executable paths are retained only in an explicitly
historical protocol-evidence report. New commands use repository-relative paths.

The staged file inventory contained no local environment, database, executable,
cache or build output. No obvious secret/private-key match was found in staged
release sources; example configuration retains placeholders. This is not a
guarantee of zero undiscovered secrets.

## I–J. Claim boundary and post-selection work

**Pre-selection software/evidence baseline ready to freeze.** This does not
declare all selected device integrations field-ready or all research validated.

R3 evidence-qualified perception, PV-SOE advisory, provenance and replay are
implemented and verified with deterministic synthetic fixtures. Positive
envelopes depend on research assumptions, not measured fog/braking performance.
NORMAL is a research model state, never certification or a road-clear claim.

Pending: exact delivered TI frame/profile and device/SDK bindings; released
Hailo HEF/model/media reconstruction; ESP32 physical USB/SPI/counters/clock,
fresh-boot entropy and watchdog bindings; mounted RGB/thermal/IMU/GNSS/encoder
identity, capture/correction/timing/calibration validation; field observation,
uncertainty/coverage, wheel slip and braking assumptions; Pi 5 load/timing and
operator ergonomics. Consult the existing R3 vendor/foundation reports for
exact boundaries, not the earlier powered-robot wiring diagrams.

No hardware was probed or commanded. No real-fog, production-ready,
mine-certified, HEMM braking, Hailo throughput or physical synchronization claim
is made. Traction remains **DISABLED_PHASE_1**. Browser remains monitoring-only.
Git push does not prove the public demo has been redeployed or externally verified.
