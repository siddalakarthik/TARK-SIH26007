# SIH/site submission copy

## Project title

TARK — Perception-aware safety assistance for open-cast mine vehicles.

## Problem statement

Fog and low visibility make reliable perception and timely operating decisions
difficult around mine vehicles. The engineering question is not only whether
a target is detected, but whether the available evidence can justify operation.

## Solution overview

TARK explores a Perception-Verified Safe Operating Envelope (PV-SOE): perception
evidence and stopping requirements constrain permitted operation. The current
Phase-1 release demonstrates a provisional software model with traction disabled.

## How it works

Radar observations retain source timestamps and pass through health, freshness,
slot-based tracking and a parameterized stopping/envelope comparison. The Pi
issues a bounded zero command. Protocol V2 software checks session, configuration,
sequence and receiver-local expiry. Events and recording support replay.

## Technical architecture

Local decision path: sensors → Pi software → bounded command → ESP32 software
supervisor → disabled output boundary. Monitoring path: Pi → REST/WebSocket →
shared React HMI. GNSS/map and browser device location are observational;
the browser never has motion authority. Independent E-stop/contactor isolation
is an electrical design, awaiting physical verification.

## Key software evidence

Controlled production-path scenarios exercise stale/future observations,
valid-empty versus missing data, communication loss, late responses, restarts,
reconnects, observer independence and replay. The current release's
[dated test/evidence record](TEST_REPORT.md) supplies counts and scope.
These are software results, not vehicle or mine trials.

## Innovation / differentiation

Our proposed system-level differentiation is perception evidence constraining
permitted operation. We do not claim radar, EKF, TTC, watchdogs or E-stops as
individual inventions. Separate numerical studies explore adaptive covariance;
production multisensor fusion is not claimed.

## Current prototype scope

TARK PHASE-1 SOFTWARE EVIDENCE RELEASE R1 integrates software interfaces,
decision logic, Protocol V2, monitoring and evidence tools. All commands stay
zero. Physical hardware integration, calibrated perception, braking and fog
tests belong to the next controlled phase.

## Future scale-up

First close purchased-part/electrical HOLDs and board integration, then measure
sensor/vehicle behavior under reviewed conditions. Higher-grade components
and operational trials require new engineering evidence, not a software-only
maturity claim.

## Safety architecture

Monitoring, local decisions, bounded supervision and intended independent
physical isolation are separate responsibilities. NORMAL is a modeled state,
not certification. No autonomous driving, collision guarantee or mine readiness
is claimed.

## Demo URL wording

[Public software demonstration](https://tark-sih26007-demo.onrender.com):
simulation and monitoring only. Historical availability is recorded; current
availability and deployed commit were not checked during R1. This local release
has not been pushed or deployed.

## GitHub wording

[Project source repository](https://github.com/siddalakarthik/TARK-SIH26007):
remote configured in this checkout. Access/visibility is not asserted here.
The R1 commit/tag are local until separately authorized publication; do not
describe the remote as already containing them.
