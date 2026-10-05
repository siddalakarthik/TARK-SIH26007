# TARK project status

Current identity: **TARK PHASE-1 SOFTWARE EVIDENCE RELEASE R1**.
See the [manifest](TARK_RELEASE_MANIFEST.md) for exact commits and counts.

## What TARK is

TARK proposes perception-aware safety assistance for open-cast mine vehicles
in fog and low visibility. PV-SOE links the quality of available perception
evidence to the operating envelope that could be justified. That is the
system-level engineering approach, not a patent or world-first claim.

## What exists today

A single application combines radar decoding, normalized observations,
health/freshness, slot-based tracks, a provisional stopping/envelope comparison,
bounded zero commands, Protocol V2 host/firmware supervision, persistence,
recording/replay and a monitoring HMI. GNSS, RGB, IMU and thermal interfaces
are configured observational boundaries with simulated/mocked test coverage.

The production pipeline uses radar evidence. It does not implement EKF,
cross-sensor fusion, calibrated free-space observability, autonomous steering
or a TTC-driven policy. `D_env` is nearest active radar range minus the stored
uncertainty, clamped at zero. Stopping calculation currently assumes zero
vehicle speed. These are software-model limits, not measurements.
NORMAL is the current modeled decision state, not permission to move.

## What has been software-verified

Controlled regressions cover old/future evidence, valid-empty versus missing
reports, one runtime owner independent of observers, session-bound communication,
expiry/reconnect, recording checkpoints and full-session replay. Prompt-3's
20 scenarios/150 repetitions preserved zero commands and deterministic logical
traces. The [evidence report](DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md) states
the exact compared fields; host tests are not board tests.

## What has been studied separately

Supplied research packages examine stopping-envelope assumptions, fixed versus
quality-adaptive covariance EKF and fault-state logic. They are **RESEARCH /
SIMULATION STUDY**, not imported production policy. The EKF study reports
condition-dependent results using synthetic quality inputs, not measured
LD2450/thermal quality. See [reference inventory](../release/references/README.md).

## What is designed and what is on HOLD

The five-sheet electrical package defines intended wiring, including independent
NC E-stop/contactor isolation. It is **CONTROLLED DESIGN / PRE HARDWARE
COMMISSIONING**, not released for energization or PCB fabrication. All 27
HOLD items remain: purchased variants, fuse ratings, converter topology/return,
coil/driver/suppression, sensor and encoder supplies, connectors and PCB details.

ESP32 USB/scheduler/fresh boot identity and hardware watchdog binding require
reviewed board integration; these are not silently provided by `app_main`.
Physical sensors, wheel response, motors, E-stop, braking and fog performance
are unverified. No physical commissioning occurred in this pass.

## Next phase

Follow [PHYSICAL_VALIDATION_NEXT_PHASE](PHYSICAL_VALIDATION_NEXT_PHASE.md):
close purchased-part/HOLD records, then separately authorize bench integration
and measured vehicle trials. No percentage is used as a maturity shortcut.
Traction remains `DISABLED_PHASE_1`; permitted speed/left/right remain zero.
