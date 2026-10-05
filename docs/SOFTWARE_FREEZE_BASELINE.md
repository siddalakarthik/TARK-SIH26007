# TARK SIH26007 Software Freeze Baseline

> HISTORICAL BASELINE — SUPERSEDED BY LATER RED-TEAM / CORRECTION RELEASE.
> Retained as a dated record, not current completion or protocol authority.
> Use [R1 release index](TARK_RELEASE_INDEX.md),
> [Protocol V2](ESP32_PROTOCOL_V2.md) and
> [supersession register](TARK_SUPERSESSION_REGISTER.md).

Freeze date: 2026-09-20  
Frozen software commit: `2d319e7` — `FINALIZE SOFTWARE AND COMMUNICATION STACK`  
Previous QA commit: `962365e` — `Fix confirmed public QA issues`  
Baseline tag: `tark-software-freeze-2026-09-20`

This release is frozen as the stable TARK software baseline. The freeze is
not permanent. Future development may be reopened through a new branch or
subsequent commit while preserving this baseline.

## Current maturity

The Raspberry Pi/backend, dashboard, simulation, replay, sensor boundaries,
LD2450 software parser, encoder contract, Protocol V1 implementation and ESP32
host-test boundary are software verified. The released system remains a
research prototype: physical hardware, field behavior, calibration and
mine-certification are not claimed.

## Verified release results

- Backend: **97 passed**.
- Frontend: **25 passed**.
- TypeScript: **passed**.
- Production build: **passed**.
- Protocol V1 Python tests: **passed**.
- Firmware host tests: **passed**.
- Public Render deployment: the repository contains the Render Blueprint and
  public-demo configuration; no provider-assigned public hostname is recorded
  or independently verified in this repository.
- Current public URL: **NOT RECORDED / NOT VERIFIED**. Do not infer or invent a
  URL from the service name in `render.yaml`.

## Safety state

- `TRACTION = DISABLED_PHASE_1`.
- The browser has no motor authority and the public dashboard is
  monitoring-only.
- Simulation sources remain explicitly labelled.
- Physical hardware is not claimed as verified.
- The physical E-stop remains an independent hardware safety path.

## Hardware-dependent items

The following still require controlled physical evidence: LC29H/GNSS identity
and serial behavior; LD2450 device identity, serial output and calibration;
ESP32 board identity, flashing and USB exchange; encoder electrical interface
and counts; MDD10A, motors, contactor and E-stop behavior; camera, thermal and
IMU calibration; and vehicle-level validation.

## Future development items

Future work may add verified hardware adapters, calibration, field validation,
performance improvements, deployment changes, or new features. Such work must
preserve the baseline as a rollback/reference point and must not imply physical
verification without evidence.

## Reopening development

Use this exact workflow:

```text
FROZEN BASELINE
      ↓
Create new development branch
      ↓
Implement new change
      ↓
Run regression tests
      ↓
Review diff
      ↓
Create new release commit
      ↓
Deploy new version only after verification
```

Example:

```powershell
git switch -c feature/<short-description> tark-software-freeze-2026-09-20
# implement and test the change
git diff
git status
git commit -m "Describe the verified change"
```

Do not overwrite history, force-push, squash away the frozen baseline, or
modify the freeze tag. The tag and commit remain available as the stable
rollback/reference point.
