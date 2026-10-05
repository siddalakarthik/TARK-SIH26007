# SIH26007 requirement-driven engineering study

This is an isolated research layer on R1, not a new production controller. No
hardware APIs or live application modules are imported. Live traction remains
`DISABLED_PHASE_1`. Physical validation is pending.

## Reproduce

Use a separate Python environment (tested Python and exact versions recorded in
manifest.json). From the repository root:

```text
python -m pip install -r studies/sih26007_simulation/requirements.txt
python -B studies/sih26007_simulation/run_all.py
python -B studies/sih26007_simulation/run_all.py --verify
```

The first command installs only research dependencies in your chosen environment.
The runner reads declared JSON inputs, generates CSV, renders PNG/SVG from CSV,
independently verifies arithmetic, runs study tests, writes reports, manifest and
SHA-256 fingerprints. It overwrites only its own generated artifacts and eight
named study reports under docs. Verification returns nonzero on failed checks.
No network or hardware is used during a study run. Do not edit a generated report
without updating its generator and regenerating the inventory.

Results and exact row selectors: `results/final_simulation_summary.json`.
Main narrative: `../../docs/TARK_SIH26007_SIMULATION_REPORT.md`.
Research row counts include assessments, not unique physical trials. Blank CSV
cells mean not applicable/not computed, never zero by implication. Invalid
unconstrained candidates are retained, not removed to improve the findings.

## Evidence scope

Read SIH_REQUIREMENTS_TRACEABILITY.md and SIMULATION_SELECTION_MATRIX.md first.
Official downloads were obtained 2026-09-29. The PS excerpt preserves the fetched
source, including its encoding artifacts. Original full-page SHA-256 is retained;
only the exact relevant modal is archived, not thousands of unrelated PS entries.
Four metres is a derived visual midpoint. None of the official sources supplies
the study's assumed braking, latency, uncertainty, trustworthy range or cycle
fractions. No simulation tool mandate was found in the reviewed material.

## R1 regression (separate from study)

With existing backend dependencies installed and project test configuration:

```text
python scripts/run_evidence_harness.py --verify evidence/prompt3
python -m pytest -q
cd frontend
pnpm test
pnpm run lint:types
pnpm run build
```

Full backend tests include protocol, replay, evidence and strict freshly compiled
C firmware host fixtures. They use software fakes, not attached devices. Do not
start runtime hardware adapters. Use an in-memory database and clear any local
TARK hardware environment overrides before testing. Compiler/platform warnings
and exact results belong in reports/QUALITY_GATE.md, not assumptions.

## Interpretation

No small-prototype scaling to mine HEMM is asserted. Encounters are 1D finite-
horizon point-gap kinematics. Timelines are condition assessments, not physical
speed trajectories. Negative-margin uncertainty share is not accident probability.
Cycle/throughput indices are normalized conditional comparisons, not MTPA.
All electrical HOLDs and physical-validation requirements remain intact.
