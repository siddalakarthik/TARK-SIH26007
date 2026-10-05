# Master-2 — validation and evidence plan

**Tests specified, not executed in this documentation pass.** Physical work requires separate authorization, competent supervision and completed power/mechanical gates. No test result is fabricated from a design target.

## 1. Staged release gates

| Gate | Scope | Exit requirement |
|---|---|---|
| G0 Design review | Source/contract/component/budget audit | Three handoff boundaries preserved; no uncosted sensor or false maturity claim |
| G1 Unpowered as-built review | Labels/photos, mechanical measurements, battery/charger/ratings, continuity | Detail register complete enough for a reviewed wiring/mount drawing; no physical GPIO guess |
| G2 Power-only bench | Qualified source, converters, protection, inrush, returns/backfeed | Measured branch behavior within documented limits; traction disconnected |
| G3 Sensors/compute, no traction | Identity, acquisition, timestamps, errors, recording | Actual source provenance and measured interface reliability; no fake samples |
| G4 Software/shadow integration | New adapters/algorithms with synthetic and recorded evidence | Regression, contract, replay, fault and performance gates; current commands zero |
| G5 Restrained low-energy model | Separately approved GPIO/enable/physical interruption and firmware binding | Demonstrated zero/reset/expiry behavior first; controlled wheel response and stop/coast evidence |
| G6 Outdoor localization/cooperation | Marked course, two physical rovers and base | Reference uncertainty, fix/link quality and conflict-warning measurements |
| G7 Controlled aerosol experiment | Permitted equipment/ventilation/reference method | Repeatable condition and matched clear/aerosol records; explicitly not mine validation |
| G8 Industrial progression | OEM/site/qualified safety stakeholders | Separate hazard analysis, deployment engineering, approvals and representative field evidence |

G5 is not implicitly approved by completion of G4. R1 remains `DISABLED_PHASE_1` until a separately authorized release; M2 changes no phase configuration.

## 2. Requirement-linked verification matrix

| Test | Requirement / failure coverage | Procedure / evidence | Acceptance basis |
|---|---|---|---|
| V01 Identity and selection | M1 selections, three handoff boundaries | Compare actual labels/revisions/configuration to frozen list | No undisclosed substitution; unresolved GPIO/assembly remains HOLD |
| V02 Power and return paths | R14/R15, F18–F20 | Reviewed unpowered then qualified bench measurements | Rated limits respected; no alternative motor-energy path around disconnect |
| V03 Startup/reset/expiry | R09/R13, F16–F19 | Host tests then separately approved actual board binding, reset/disconnect/clock faults | Current outputs zero; later safe physical behavior measured, not inferred from ACK |
| V04 Radar reference geometry | R01, F01/F02 | Known targets, distances/lateral positions/velocities and profile IDs | Error/coverage/false-alarm report; no maximum-range guarantee |
| V05 RGB calibration/detection | R02, F03 | Held-out scenes, several distances/light levels, actual exposure modes | Calibrated geometry and task metrics; manual-control/FOV claims match evidence |
| V06 Thermal acquisition/contrast | R03, F04 | Actual frames, FFC, safe references, association cases | Reported native timing/quality; no invented range/temperature accuracy |
| V07 Sensor association | R01–R03, F05 | Radar-only/RGB-only/thermal-only, occlusion and overlapping targets | Wrong associations/rejections quantified; disagreement retained |
| V08 Localization | R04/R06, F06–F08 | Outdoor reference course, stationary/moving/occluded conditions | M1 <=0.10 m horizontal-error goal assessed only with adequate reference; otherwise limited repeatability result |
| V09 Wheel sensing | R07, F09/F10 | Calibrated rotation, reverse, missing samples, injected invalid flags and slip cases | Signed response correct within measured bounds; wrap ambiguity cannot become confident distance |
| V10 Map matching/guidance | R04/R05, F13 | Adjacent edges, junction ambiguity, closure/revision mismatch and route deviation | No confident wrong-road instruction in specified rejection cases; course/reference scope explicit |
| V11 Cooperative conflict | R05/R12, F07/F11/F12 | Two marked approaches, stopped/receding peers, packet delay/loss | Conflict intervals and warning lead time measured; silence never grants clearance |
| V12 Clock provenance | R01–R13 | Source reboot, unknown epoch, rollback/future time, delayed transport | Invalid timing rejected; publish/poll does not refresh sensor age |
| V13 Operating envelope | R01/R07/R09, F01–F20 | Synthetic parameter sweeps, faults, ambiguous speed and uncertain coverage | Monotonic non-increase under increased uncertainty/removed evidence; current output always zero |
| V14 Offline failures | R12/R13 | Remove internet, then observer/browser, then AP | Local path independent where required; cooperative/correction loss explicitly shown |
| V15 API/WebSocket integrity | R10/R12 | Wrong types/null/NaN/oversized/out-of-order/disconnect; multiple clients | No false healthy/current values, bounded resources, no browser authority |
| V16 Replay/evidence | R11, F21/F23 | Full recorded sessions, checkpoints, interruption/corruption/incompatibility | Isolated replay; full coverage and compared fields stated; incomplete sessions not blanket MATCH |
| V17 Resource stress | R08/R11/R12, F14/F15 | Concurrent inference/acquisition/recording/HMI, slow consumers and storage pressure | Measure CPU/GPU/RAM, queue depth, drop counts and p50/p95/p99 latency; required evidence expiry remains effective |
| V18 Driver/control-room UX | R10, F22 | Required viewport widths, physical display, stale/unknown/stop and long-text cases | State/action/reason understood; no overflow/zero-height map/colour-only warning |
| V19 Security/authority | R09/R13, F24 | Unauthorized observation/route/config requests, forged peer identity, replay | Reject unauthorized mutation/identity, no credentials leaked, no motor command path in browser |
| V20 Mechanical/calibration retention | R16 | Weigh/layout review, mount/remount and controlled vibration | Payload/CG/clearances acceptable; calibration changes detected and recorded |
| V21 Artificial aerosol | R17 | Matched repeated target/condition trials with optical references | Report limits/errors and condition, not a claim of recreated monsoon |
| V22 Budget and claim audit | R18, industrial limits | Reconcile allocations, source/measurement labels and R1/R2 maturity | No added premium sensors; headroom reserve preserved; no unsupported impact/verification claim |

The matrix references M1 requirement IDs R01–R18. Qualitative gate criteria become measurable tolerances in an approved test protocol before data is inspected. Do not choose a passing tolerance after observing failures.

## 3. Scenario and data design

Include stationary, approaching, receding, crossing and multiple targets; reflective/cluttered scenes; day/low light; clear/aerosol; different target orientations and thermal contrast. Compare matched cases with held-out repeats. Keep safe distances and use props/reference fixtures for initial work, not people in a motor path.

Record target type/position/reference uncertainty, sensor/profile/exposure/calibration versions, ambient condition, acquisition/receive times, dropped frames, health, decisions, requested/accepted/applied status and original source mode. Distinguish true labels measured independently from estimates generated by TARK itself. The system cannot serve as its own accuracy reference.

No source absent from a run is marked tested. Manufacturer specifications are not run measurements. Mocked tests validate software handling, not physical RF/optical/USB performance.

## 4. Timing and performance measurement

Measure acquisition-to-normalization, normalization-to-decision, request-to-correlated-ACK and decision-to-HMI separately. A host round-trip does not prove actuator motion latency. Independent clock epochs require mapping/bounds; the Protocol V2 duration contract is not a physical network-latency measurement.

Record p50/p95/p99 plus worst observed latency, duration, workload, temperature/power state and sample count. Long-tail timing matters. M1 peer age <200 ms p95 is a design target under defined load, not an accepted worst-case bound. A 20 Hz decision task does not make the slower camera/thermal observations 20 Hz fresh evidence.

Test capacity up to the declared bounded track/peer/event/recording limits, then one step beyond. Overflow must be explicit and bounded. Test slow clients without starving acquisition; replay and media work must not acquire local motion authority.

## 5. Statistical and human-factors honesty

Report counts and uncertainty, not only best-case demonstrations. Estimate detection probability, false alarms per defined time/distance/opportunity, classification precision/recall, localization error percentiles, association errors, warning lead time and nuisance-warning rate. Use independent trials and document correlations; many frames from one trajectory are not many independent trials.

Zero observed failures is not zero risk. As a rough binomial illustration, zero failures in n independent trials gives an approximately 3/n upper 95% failure-probability bound; dependence and selection bias invalidate that shortcut. Industrial safety cannot be established by this statistic alone.

For driver tests, ask participants to identify current state, required action, reason, source mode and stale information. Measure task success/time and workload with consent. No simulator response-time result is automatically real-cab operator performance.

## 6. Evidence release

Every report includes scope, software/hardware/configuration IDs, raw/normalized record references, reference method/uncertainty, exclusions, failures, analysis procedure and reviewer. Preserve original data; label recomputation. Publish only permissioned/redacted imagery. A software PASS, bench PASS and industrial validation are distinct evidence levels.

This pass executed documentation/link/arithmetic/scope checks only. It did not run these proposed experiments or rerun historical backend/frontend/firmware suites.
