# TARK — SIH26007

Perception-aware safety-assistance research for mine vehicles in low visibility.

## Current: R3 SIH pre-selection software baseline

Start with [the pre-selection freeze](docs/TARK_R3_PRESELECTION_FREEZE.md),
[three flagship demonstrations](docs/SIH_FLAGSHIP_DEMOS.md), and the current
[R3 reasoning report](docs/R3_REASONING_REPORT.md). R3 adds a separately labelled,
evidence-qualified research advisory; the legacy decision/control path is retained.
Conditional R3 TTC uses qualified successive positions under explicit research
assumptions, not Doppler as a velocity vector. Neither advisory nor browser can
command motion. Traction remains `DISABLED_PHASE_1`.

```powershell
# From the existing installed project environment; no hardware required
.\.venv\Scripts\python.exe scripts/run_sih_demos.py --scenario all
$env:TARK_HARDWARE_PROFILE='R3_PI5_ADVISORY'
$env:TARK_R3_FIXTURE_PATH=(Resolve-Path 'data\fixtures\r3_sources_v1.json').Path
.\scripts\run_demo.ps1
```

Open `http://localhost:8000/#/safety`; Driver is `/#/hmi`, Diagnostics
`/#/diagnostics`, Replay `/#/replay`. The dashboard fixture is intentionally
uncommissioned/UNKNOWN, not the positive-envelope CLI research demo. See
[local setup and optional Windows dependency selection](docs/R2_WEBSITE_RUN.md).

Tests: `python -B -m pytest backend/tests -q -p no:cacheprovider`; from
`frontend`: `pnpm test`, `pnpm run lint:types`, `pnpm run build`.
Artifacts go outside the repository to `../work/sih_preselection`; existing
outputs are never overwritten. Choose a fresh `--output` to repeat a run.

**Claim boundary:** R3 normalized-evidence reasoning/replay is software verified
using deterministic synthetic fixtures. Hardware, Hailo inference, real fog,
sensor synchronization, HEMM braking and mine certification remain unverified.
See [R3 foundation/vendor boundaries](docs/R3_SOFTWARE_INTEGRATION.md) and
[physical work](docs/PHYSICAL_VALIDATION_NEXT_PHASE.md). No public deployment is
updated by the Git freeze alone.

## Historical R1 release (retained, not current R3 status)

**TARK PHASE-1 SOFTWARE EVIDENCE RELEASE R1** is a controlled software-evidence
baseline, not an as-built vehicle release. `DISABLED_PHASE_1`: permitted speed,
left command and right command are always zero.

Start with the [release index](docs/TARK_RELEASE_INDEX.md),
[project status](docs/PROJECT_STATUS.md) and [manifest](docs/TARK_RELEASE_MANIFEST.md).

## Architecture and implemented scope

Radar reports → source-time health/freshness → slot-based tracks → provisional
PV-SOE/stopping comparison → bounded zero command → Protocol V2 supervisor.
Events and recordings support deterministic replay. FastAPI REST/WebSocket
publish cached observations to the React/MapLibre HMI; consumers do not advance
the decision loop. GNSS, RGB, thermal and IMU have separate observational
interfaces, not production multisensor fusion.

The ESP32 C parser/service/supervisor is host-tested. Physical USB, fresh boot
identity, scheduler and watchdog bindings remain outside this release.

## Software evidence

Prompt 1 corrected stale/future evidence, runtime ownership and HMI truthfulness.
Prompt 2 established [Protocol V2](docs/ESP32_PROTOCOL_V2.md) and recording-format-2
replay semantics. Prompt 3 exercised 20 production-path scenarios over 150
independent repetitions. See the [current test record](docs/TEST_REPORT.md)
and [claim/evidence matrix](docs/TARK_CLAIM_EVIDENCE_MATRIX.md).

## Run the local software demo

From this repository in PowerShell, with Python and the pinned frontend tools installed:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\scripts\build_frontend.ps1
.\scripts\run.ps1
```

Open `http://localhost:8000`. The checked-in configuration is simulation;
leave device paths/identity evidence unset. See [RUN](docs/RUN.md) and
[deployment profiles](docs/PUBLIC_DEPLOYMENT.md) for the environment contract.
Use a single application worker for one TARK instance.

## Reproduce the evidence

In the installed project Python environment, with no hardware configuration inherited:

```text
python scripts/run_evidence_harness.py --verify evidence/prompt3
python -B -m pytest -q -p no:cacheprovider
```

From `frontend`: `pnpm test`, `pnpm run lint:types`, `pnpm run build`.
Fresh strict GCC host tests run inside the Python protocol fixture. See
[evidence authority](docs/EVIDENCE_AUTHORITY.md) for isolation, fingerprinting
and reproducibility limits. Do not overwrite the supplied evidence bundle.

## Public demo is not physical vehicle control

[Recorded public software demonstration](https://tark-sih26007-demo.onrender.com)
is simulation/monitoring only. Its availability and deployed commit were not
rechecked during this local release pass. This local R1 has **not been pushed
or deployed**. A browser cannot command traction.

PV-SOE is currently a simplified provisional model. Vehicle speed is not
measured; TTC is **NOT COMPUTED** in production decisions; WARN has no executable
production policy. Research EKF/fusion studies are separate. No measured
braking, fog, E-stop, physical watchdog or mine-certification claim is made.

## Repository

`backend/` contains the application and tests; `frontend/` the monitoring HMI;
`firmware/esp32/` the board-neutral C stack; `config/` reviewed parameters;
`simulation/` fixtures; `scripts/` operating tools; `docs/` controlled guidance;
`evidence/prompt3/` immutable software evidence; `release/` release identity and
read-only historical/design references.

Physical work starts with the [next-phase gates](docs/PHYSICAL_VALIDATION_NEXT_PHASE.md)
and [electrical HOLD register](release/references/electrical/HOLD_REGISTER.md),
not a software test pass. Historical freezes remain in the
[supersession register](docs/TARK_SUPERSESSION_REGISTER.md).
