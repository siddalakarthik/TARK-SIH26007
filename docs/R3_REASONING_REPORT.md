# TARK R3 — evidence-qualified perception and advisory

Controlled software handoff · 5 October 2026 · SIH26007

## Result and claim boundary

R3 evidence-qualified perception and PV-SOE advisory architecture is implemented
and verified using deterministic fixtures. This is a parallel research advisory,
not a replacement for the legacy decision engine and not a motor controller.
Traction remains `DISABLED_PHASE_1`. No physical device was accessed.

All positive numerical envelopes in the demonstration depend on explicitly
synthetic calibration, clock, coverage, motion and vehicle assumptions. The
normal application default remains uncommissioned: missing qualified geometry
or coverage produces UNKNOWN. An empty radar frame does not establish clearance.

This report consolidates requested outputs B–R. Output A is the prior
[adversarial design review](R3_REASONING_DESIGN_REVIEW.md). Older foundation
reports describe earlier milestones; they are not the current reasoning status.

## B. Architecture

```text
Existing admitted TARK_EVIDENCE_1 channel
  → current health / freshness / clock / calibration checks
  → purpose-specific semantic observations
  → bounded local tracks + calibrated image associations
  → observability + body corridor + conditional relative motion
  → transparent hazards + separate cooperative context
  → parameterized stopping requirement + R3 state machine
  → TARK_R3_ADVISORY_1 + deterministic Why?
  → existing snapshot/API/WebSocket + recording
  → isolated R3 recomputation

Legacy sensor pipeline → legacy decision / zero-output command (unchanged)
```

`reasoning_models.py` owns versioned contracts; `reasoning.py` is a pure,
deterministic reasoning boundary without device I/O or control calls.
`R3Runtime.capture()` runs it inside the existing snapshot/recording lock. There
is no additional safety thread, socket, browser authority or actuator path.
Execution timings are outside deterministic decision records.

## C. Sensor semantics and allowed purposes

DISPLAY is permitted only for fresh, producing, structurally valid observations.
Other grants additionally require the existing source qualification checks.

| Evidence | Additional permitted purposes | Explicit exclusion |
|---|---|---|
| TI radar | RANGE, TRACK_ASSOCIATION, PVSOE_INPUT after body calibration and bounded position error; RADIAL_VELOCITY when its bound exists | No Doppler-to-vector substitution, automatic object class or road-clear claim |
| RGB | PVSOE_INPUT for configured coverage; SEMANTIC_CLASSIFICATION with versioned research model metadata | Pixel confidence does not establish metric distance or fog range |
| Thermal | Configured corroborative coverage and qualified semantics; FFC must be IDLE | No identity claim, automatic range or fabricated temperature |
| Own GNSS | LOCALIZATION with a fix and position uncertainty | Never local obstacle range or stationary course-as-heading |
| Node B GNSS | LOCALIZATION; COOPERATIVE_CONTEXT only under correction/uncertainty policy | Never a local radar point or detection of unequipped vehicles |
| IMU | EGO_MOTION with downstream angular-rate checks | No unqualified body-frame motion estimate |
| Encoders | EGO_MOTION with explicit count convention, scale and uncertainty | Wheel response is not ground-truth vehicle speed |

Semantic observations retain evidence/source IDs, capture estimate and error,
age bound, source mode, frame, units, calibration references, measurement and
lineage. Large thermal grids remain in the original evidence/media reference,
not duplicated into the reasoning summary. There is no generic qualified=true
shortcut granting every computational purpose.

## D. Observability

Coverage is a separate, versioned assumption, not inferred from target count.
For each required hazard class, take the maximum justified range among eligible
supporting modalities. The forward envelope is the minimum of those class
ranges. A missing class makes the envelope UNKNOWN.

For an eligible source:

`range_lower = max(0, configured_range × environment_factor − range_uncertainty − position_uncertainty)`.

The configured half-angle must cover the full body corridor at its near boundary.
RGB uses GOOD / DEGRADED / SEVERE factors; UNKNOWN environmental provenance
provides no RGB coverage. Generic fog does not arbitrarily weaken radar or
thermal. Range provenance is MEASURED, CONFIGURED_RESEARCH or UNKNOWN. A
MEASURED label requires externally reviewed measurement evidence; this software
does not turn a supplied reference string into physical validation.

The demonstrator uses synthetic 15 m RGB and 3 m radar coverage, not product
specifications. At the configured bounds these become 14.79 m and 2.79 m.
Thermal has no invented default coverage. Dynamic occlusion/free-space mapping
is not claimed; configured coverage assumes its stated research visibility
domain. Local hazards constrain capability independently of the coverage label.
`road_clear_claim` is always false.

## E. Tracks and association

`TARK_R3_TRACK_1` uses bounded, deterministic, unambiguous nearest-neighbour
association. A candidate must share source/mode and lie inside the configured
gate plus both position-error bounds. Multiple candidates do not force a match.
No Kalman filter, covariance, persistence probability or hidden identity is
invented. NEW becomes CONFIRMED on an unambiguous subsequent measurement.
Missing/currently held measurements become COASTING; no current velocity is
asserted for them. Tracks expire after the configured lifetime.

Positions require an explicit source-to-body transform: x forward, y left,
z up. Position uncertainty includes configured sensor and calibration error.
The default capacity is 32 tracks (maximum configurable 64). More incoming
points than capacity produces UNKNOWN rather than trusting a convenient subset.

RGB/thermal association uses calibrated inverse extrinsics, pinhole intrinsics,
capture-time bounds, matching source modes, FOV, projected position uncertainty
and image boxes. Outcomes remain ASSOCIATED, POSSIBLE, UNRESOLVED or CONFLICTING.
Track contributors and semantic evidence IDs preserve the association lineage.
Incompatible class evidence is visible, not averaged away. Unresolved image
hazards cannot quietly imply clearance: their metric geometry remains unknown.
No range is derived from a bounding box alone.

## F. Relative motion and TTC

Radar radial velocity remains its own field. Two calibrated body positions can
provide `(position_now − position_previous) / dt` only under the explicitly
enabled fixed-body-axes research model, qualified low angular motion, bounded
timing, a permitted sampling interval and a velocity-error ceiling. Position,
timing, angular-rate and configured acceleration allowances contribute to the
velocity bound. Absolute target velocity remains unavailable.

TTC uses a positive lower bound on forward closing speed, relevant corridor
geometry, and a configured finite prediction horizon. Its interval divides
bounded clearance by bounded closing speed; the point estimate uses the same
conditional constant-relative-motion model. Lateral uncertainty must remain
inside the corridor over the interval. These are conditional model bounds, not
a guarantee against arbitrary acceleration. Insufficient motion, coasting,
uncertain lateral intersection or excessive horizon returns null with a reason.
Unknown is never encoded as zero or infinity.

## G. Corridor relevance

The local body corridor has explicit width and near/far extents. Uncertainty
that straddles its boundary produces UNKNOWN relevance. An initially outside
track whose bounded motion can cross the corridor is not discarded as harmless:
it becomes an uncertain crossing candidate. Map and GNSS context cannot override
this local calculation. No map is required for the configured body-frame model.
The default corridor is absent, so the uncommissioned system cannot infer one.

## H. Cooperative context

Node B remains a separate context list. Its own position, uncertainty, age,
source mode, correction quality and evidence reference are retained. A potential
conflict requires both qualified positions to overlap a configuration-defined
geographic conflict zone, including uncertainty. This is a small-area research
zone-overlap test, not exact collision distance, inferred road topology or TTC.
No conflict zone is invented from the background map.

The fixture zone is synthetic and unsurveyed. Stale, correction-unqualified or
excessively uncertain B is removed. Loss of previously supporting peer evidence
causes a conservative hold/UNKNOWN; it does not leave a ghost vehicle or silently
release the previous restriction. Unequipped hidden vehicles are not detected by
cooperative positioning.

## I. PV-SOE definition

For bounded wheel response `v_upper = response + response_uncertainty`:

`D_stop = v_upper × response_time + v_upper² / (2 × deceleration) + margin`.

For justified distance D, the inverse research ceiling is:

`v_cap = max(0, −a×t + sqrt((a×t)² + 2×a×max(0,D−margin)))`.

Clamp this by the versioned vehicle maximum, applicable local-hazard range and
cooperative restriction. UNKNOWN capability has a null ceiling; STOP has zero.
This is advisory mathematics, not a traction command. The browser only displays
the result. The contract names SMALL_SCALE_POC, R3_RESEARCH_CART and
HEMM_REFERENCE_MODEL; selecting a name does not supply validated vehicle data.
HEMM deployment requires OEM/field evidence, not scaled-up student-cart values.

## J. State machine and monotonicity

| State | Meaning / entry |
|---|---|
| NORMAL | Qualified configured research envelope supports the operating model |
| WARN | Degradation exists but the remaining research ceiling is adequate |
| RESTRICT | Reduced ceiling, relevant local hazard or qualified cooperative conflict |
| UNKNOWN | Evidence, motion, relevance, association or processing completeness cannot justify capability |
| STOP | No positive envelope, critical local distance or unmet stopping condition |

State severity order is NORMAL → WARN → RESTRICT → UNKNOWN → STOP. Degradation
is immediate. Recovery requires both configured distinct accepted frames and
dwell (defaults: 3 frames and 500 ms), restored supporting quality, and no new
degradation. Polling the same evidence does not count as recovery. A persistent
loss retains its original quality target rather than forgetting the loss after
a few cycles. This deliberately sacrifices availability; there is no automatic
operator override in this phase.

Mixed REAL/SIMULATION qualified inputs cannot justify a combined envelope.
Publication beyond the decision deadline projects UNKNOWN, or retains STOP if
already stopped. Stale publication cannot relax STOP or mutate the saved record.
Capability monotonicity is tested over losses, increasing uncertainty, reduced
range, time/calibration faults and cooperative expiry. This is tested coverage,
not a mathematical proof for every possible physical world.

## K. Decision and explanation contracts

`TARK_R3_ADVISORY_1` contains evaluation/deadline times, state, action, nullable
ceiling, vehicle profile, observability, semantic observations, tracks, TTC,
hazards, separate peers, exclusions, calibration/configuration references and
software fingerprint. Lists are bounded, numeric values finite, and fields are
strictly validated. Checkpoints have their own strict versioned schema.

`TARK_R3_WHY_1` supplies deterministic primary reason, action, supporting IDs,
exclusions, track/peer IDs, unresolved semantics, required range and qualified
range. It is not generated by an LLM. The UI has no parallel safety calculation.

## L. Required scenario matrix

All 25 scenarios below passed. States are endpoint expectations after the
specified fixture sequence, not universal labels for similarly named situations.

| # | Scenario | Expected state |
|---|---|---|
| 1 | Healthy, empty radar, explicit research coverage | NORMAL |
| 2 | Stationary obstacle inside critical distance | STOP |
| 3 | Lead moving target | RESTRICT |
| 4 | Approaching/oncoming target reaching stopping boundary | STOP |
| 5 | Crossing candidate outside current corridor | UNKNOWN |
| 6 | Severe RGB visibility degradation, radar valid | RESTRICT |
| 7 | Radar stale, other configured coverage remains | WARN |
| 8 | RGB unavailable | RESTRICT |
| 9 | Thermal unavailable | WARN |
| 10 | Multiple sources degraded | UNKNOWN |
| 11 | All geometry unavailable | UNKNOWN |
| 12 | Radar calibration invalid; other coverage remains | WARN |
| 13 | Clock mappings expired | UNKNOWN |
| 14 | Target uncertainty exceeds geometry gate | UNKNOWN |
| 15 | Duplicate frame followed by expiry | UNKNOWN |
| 16 | Out-of-order frame followed by expiry | UNKNOWN |
| 17 | Radar/RGB geometry disagreement, unresolved image hazard | UNKNOWN |
| 18 | Node B shares synthetic blind-curve zone | RESTRICT |
| 19 | Node B stale | UNKNOWN |
| 20 | Node B uncertainty too high | UNKNOWN |
| 21 | Cooperative correction lost | UNKNOWN |
| 22 | Map unavailable, qualified local model remains | NORMAL |
| 23 | Wheel-response speed exceeds ceiling | RESTRICT |
| 24 | Lower configured deceleration | RESTRICT |
| 25 | Sustained recovery after degradation | NORMAL |

## M. Tests and adversarial corrections

Final backend: **489 passed, 0 failed, 0 skipped**, 83.511 s. Includes the C
encoder-observation host interoperability test. A previous foundation run was
OS-blocked; that historical failure is not deleted, but the current host test
ran successfully. No Windows protection setting was changed.

Final frontend: **166 passed** across 15 files. TypeScript and production build
passed. The existing lazy MapLibre bundle still emits the >500 kB chunk warning.
Backend reports three dependency deprecation warnings; none is disguised as
a failed or skipped test.

Regression additions cover nullable TTC, no Doppler vector fabrication, no GNSS
radar range, duplicate/order rejection, calibration/clock exclusion, distinct
recovery frames, no ghost peers, monotonic loss/uncertainty/range sweeps, mixed
source modes, track capacity, classification disagreement, coasting, replay
isolation/corruption/version rejection, publication expiry and HMI validation.

Bugs found and corrected during this phase:

- Peer speed limit could be skipped after another restriction: always apply the
  tighter peer ceiling while its evidence remains valid.
- Long loss could be forgotten during recovery: retain the pre-loss quality target.
- An approaching lateral crossing could be ignored outside the instantaneous
  corridor: check bounded future corridor intersection.
- Held tracks could retain a current-looking velocity: mark coasting and null TTC.
- Truncated target sets could appear complete: capacity overflow becomes UNKNOWN.
- Expired publication could relax STOP: keep STOP while marking evidence expired.
- Unassociated image hazards could be ignored: expose unknown semantic geometry.
- Frozen track objects and synthetic thermal projection centre needed correction;
  associations now use replacement objects and the correct fixture image geometry.

## N. Isolated replay

Record normalized observations, sessions, clocks, calibration/configuration
registries, environment, software fingerprint and initial reasoning checkpoint.
`restore_channel()` is shared by qualification and advisory comparisons; it
creates independent objects and has no live callbacks or transport references.
The R3 reasoner is the same implementation used in live software execution.

Compare the entire deterministic saved R3 decision, not just its state. Outcomes:
MATCH, MISMATCH with first sequence, or NOT RECOMPUTABLE with reason. Wrong
fingerprint/configuration, corrupt checkpoint, missing environment, malformed
decision and out-of-order records are rejected. Raw-media inference reconstruction
remains NOT RECOMPUTABLE; normalized evidence replay is not that claim.

The 300-tick demonstration produced **qualification MATCH and R3 advisory MATCH**,
with no divergence. Existing integration tests also cover SQLite recording,
legacy MATCH, API verification and R3 timeline summaries together. Replay/live
separation is tested by comparing untouched channel and reasoner state.

## O. Controlled HMI changes

Safety shows R3_ADVISORY and LEGACY_DECISION separately. Diagnostics shows R3
purpose contributions/exclusions and provenance. Driver adds only an R3 action
and short deterministic reason. Replay shows the recorded R3 summary and its
separate recomputation result. Invalid R3 data stays unavailable.

Read-only endpoint: `/api/v2/r3/advisory`. Existing snapshots/WebSocket carry the
same additive R3 field. No new WebSocket manager or map instance is introduced.
Browser review details are recorded in the verification appendix below.

## P. Demonstrators and performance

Run from the existing repository, using its installed environment:

```powershell
.\.venv\Scripts\python.exe scripts/r3_reasoning_demo.py --output ../work/r3_reasoning_new_run --ticks 300
```

The destination must be new; prior evidence is never overwritten. If this host
requires its already-reviewed Python dependency overlay, set PYTHONPATH to the
existing `../work/tark_demo_python` first, as in the recorded test commands.
No package installation or security bypass is performed by the demonstrator.

The fixture admits observations through the production ObservationAdapter and
EvidenceChannel, not a mocked decision result. It writes report.json,
metadata.json and records.json. The current evidence directory is
`../../work/r3_reasoning_evidence_final` relative to this document.

Fog demo: healthy → reduced RGB support with radar retained → reduced numeric
ceiling, not automatic STOP → lost geometry/UNKNOWN → sustained recovery.
Blind-curve demo: fresh peer conflict/RESTRICT → peer expiry/UNKNOWN and removal.
All positions, clocks, calibrations and environmental changes are SYNTHETIC.

Development PC measurements for the 300-tick empty-local-track run:

| Measurement | p50 | p95 | maximum |
|---|---:|---:|---:|
| Fixture admission + full cycle | 3.668 ms | 5.716 ms | 36.930 ms |
| Purpose/perception/association stage | 1.011 ms | 1.669 ms | 34.399 ms |
| Reasoning/decision serialization stage | 0.716 ms | 1.121 ms | 3.116 ms |

R3 replay computation: 1.475 s for 300 ticks. The synchronous reasoning queue
depth is zero; this does not measure hardware input queues. Runtime exposes track
count, cycle/perception/reasoning latency and publication age. These are Windows
AMD64 measurements, not Pi 5 latency, sustained maximum-load throughput, camera
inference performance or a hard-real-time guarantee. Capacity is also exercised
by unit tests; this timing run had no local tracks.

## Q. Remaining calibration and validation work

Still required before physical claims: device identities and selected vendor
modes; body/extrinsic/intrinsic calibration and residual bounds; clock mapping
accuracy/drift; encoder scale/count semantics/slip; radar operating domain and
detection coverage by hazard class; real RGB/thermal model evidence and confidence
calibration; PureThermal FFC/radiometry; GNSS corrections/uncertainty and surveyed
conflict zones; real Node B transport; vehicle response/deceleration; vibration,
fog, occlusion and mounting tests; Pi 5 resource profiling; operator ergonomics.

No public-road or mine deployment release is implied. Existing vendor/profile
and hardware bindings remain separately documented in R3_VENDOR_FORMATS.md and
R3_SOFTWARE_INTEGRATION.md. This phase does not invent those bindings or certify
their physical operation. Future sophistication such as general ego-motion
compensation, road free-space reconstruction and arbitrary multi-target prediction
requires a separately controlled model and evidence programme.

## R. Judge attack review

| Challenge | Auditable answer |
|---|---|
| Is this merely a collection of sensors? | Reasoning limits capability by qualified current evidence and preserves decision provenance. |
| No radar returns: why move? | Only the explicit research coverage assumption permits a positive demonstration envelope; no road-clear conclusion is made. |
| Does fog always stop the system? | No. RGB loss reduces RGB support; another qualified modality can still justify a smaller configured envelope. |
| Does radar measure the full velocity vector? | No. Doppler is radial; the separate two-position estimate has explicit restrictive assumptions. |
| Can stale V2V release a restriction? | No. Peer support disappears and capability is conservatively held or UNKNOWN. |
| Can it detect an unequipped hidden truck? | Not from cooperative GNSS. No such claim is made. |
| Why not display a confident risk percentage? | No calibrated probability model exists. Conditions, bounds and exclusions are shown instead. |
| Does replay prove perception accuracy? | No. It proves deterministic normalized-evidence recomputation under a matching software/configuration state. |
| Does NORMAL mean mine-safe? | No. It means the specified research model has sufficient qualified input; field validation remains absent. |
| Can the dashboard brake? | No. It is monitoring/advisory only and traction remains DISABLED_PHASE_1. |
| What if evidence disappears for a long time? | Recovery does not forget the lost quality requirement. Availability can remain restricted until evidence is restored. |
| Are PC timings Pi 5 proof? | No. They are development measurements with explicitly stated workload. |

## Changed-file scope

Added: `backend/app/r3/reasoning_models.py`, `reasoning.py`,
`reasoning_fixtures.py`, `reasoning_scenarios.py`;
`backend/tests/test_r3_reasoning.py`, `test_r3_reasoning_replay.py`;
`frontend/src/features/r3/R3Advisory.tsx`, `R3Advisory.test.tsx`;
`scripts/r3_reasoning_demo.py`; this report and the preimplementation review.

Extended: R3 adapters/runtime/evidence/replay; main.py read-only/replay integration;
replay/engine.py additive timeline summary; test_r3_runtime.py; .env.example;
frontend FlagshipApp, api.ts, ReplayPanel and its test, and r3.css.
Historical foundation documentation gets a supersession note only.

Pre-existing firmware, protocol, legacy UI and other dirty-tree changes were
preserved, not attributed to this phase. No commit or push was requested or made.

## Verification appendix

Test artifacts: `../../work/r3_reasoning_backend_final.xml` and
`../../work/r3_reasoning_frontend_final.json`.

Commands used: `python -m pytest backend/tests -q -p no:cacheprovider --tb=short
--junitxml=../work/r3_reasoning_backend_final.xml`; `npm test` with JSON reporter;
`npm run lint:types`; `npm run build`.

Local demo: existing `scripts/run_demo.ps1 -Port 8014`, with explicit
R3_PI5_ADVISORY profile and the existing r3_sources_v1.json simulation fixture.
The dashboard intentionally shows UNKNOWN for missing commissioned calibration
and coverage. The positive-envelope demonstration is the separately labelled
CLI fixture, not disguised as connected hardware.

Browser verification completed on 5 October 2026 at
`http://127.0.0.1:8014/`: Safety, Diagnostics, Driver and Replay loaded with
connected simulation telemetry. Safety explicitly displayed R3 UNKNOWN beside
the separately labelled legacy decision. No warning/error console entries were
captured during these checks. A browser-created recording, prefix `c73c7c17`,
contained 18 ticks across 4.78 seconds. The visible verification result was:
legacy MATCH, R3 qualification MATCH, R3 advisory MATCH; raw inference remained
NOT RECOMPUTABLE. Source labels remained SIMULATION and traction stayed disabled.

Safety DOM width checks at 320, 375, 430, 768, 1024, 1440 and 1920 pixels showed
no horizontal document overflow and a nonzero advisory panel. Driver was also
inspected at 375 pixels. This is a targeted responsive check, not certification
of every possible screen/data combination. Screenshots are saved at
`../../work/r3_reasoning_safety_browser.jpg` and
`../../work/r3_reasoning_replay_browser.jpg`. Temporary viewport overrides were
reset. Earlier transient browser-session errors were resolved without code or
security changes.
