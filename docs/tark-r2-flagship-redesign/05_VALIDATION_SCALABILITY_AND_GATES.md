# Validation, industrial scaling and release gates

Revision F0 · 2 October 2026 · Planned work, not test results

## 1. What this design can and cannot establish

The prototype can collect real range/radial-motion, RGB, thermal, GNSS and body-motion evidence under a controlled domain; test how evidence degrades; and demonstrate explainable navigation/cooperative warnings and replay after software integration. It cannot establish safe mine-haul speeds, HEMM braking performance, reduced mine accident rates, production increases, all-weather availability or regulatory certification.

No hardware has been accessed in this architecture task. No new adapter, Hailo model, radar decoder or RTK relay has been implemented by creating these documents. “Selected” never means “physically verified.”

## 2. Requirements-to-evidence plan

| Requirement | Experiment / artifact | Pass evidence required |
|---|---|---|
| Real radar geometry and relative motion | Reflector/target at measured distances; controlled approaching/receding runs | Raw processed frames, firmware/profile identity, range/velocity sign and error distribution; report missed/ghost detections |
| RGB semantics | Held-out labelled recordings across clear/obscured scenes | Precision/recall and latency by target/condition; no training-test overlap claim |
| Thermal corroboration | Known warm target and confusing backgrounds, with aligned RGB/radar | Spatial/time residuals, shutter intervals, disagreement examples; no invented temperature accuracy |
| RTK positioning | Three real kits, fixed base and reference course | Correction age, FIX/FLOAT/no-fix transitions, measured repeatability; absolute accuracy only with adequate independent reference |
| Motion estimation | Roll measured tracks, turn, lift/slip one wheel | Encoder count/direction/time, gyro comparison, invalidation behavior |
| Navigation | Local versioned graph with turns, branches and stop lines | Correct cues for valid location; ambiguous/off-route/uncertain cases visibly withheld |
| Fleet positions | A and B moving independently | Unique identities, source timestamps, quality/stale state and common coordinate reference |
| Blind-curve/junction conflict | Occluded visual path with segregated motion and physical supervisors | Predicted occupancy intervals and evidence; no unsafe close approaches to “test braking” |
| Control room | Separate laptop over local AP | Both real nodes, source ages, selected incident and connection loss indication |
| Explainability/replay | Save raw/normalized evidence with calibration/model/configuration hashes | Reproduce the decision path or explicitly report missing evidence/version mismatch |
| Offline operation | Remove internet, then separately interrupt local AP/base | Internet removal preserves local functions; loss of corrections/peer link degrades only supported capabilities |
| Power/mechanical stability | Qualified inspection, static fit and load test, thermal endurance run | Safe independent movement/braking, no exposed mains, no tip tendency, no reset/data corruption within the accepted run |
| Industrial mapping | Review with vehicle/site stakeholders | Named qualification gaps; no development-board-to-mine deployment shortcut |
| Scalability | Synthetic additional fleet nodes clearly labelled | Bounded queues, update age and bandwidth/load limits; no claim those nodes are physical |

Numerical acceptance thresholds must be set against the chosen use case before trials, not chosen after seeing results. The 1–15 m stations and ≤1 m/s cart domain are experimental limits, not a passed sensor specification.

## 3. Validation sequence

1. **Document/identity gate:** verify exact product revision, regional supply, kit contents, current price, manufacturer manuals and permitted test use. Record photographs of newly selected parts when obtained; no old-robot photos are required for this architecture.
2. **Unpowered mechanical/electrical review:** fit, mass/CG, brakes, cable protection, apertures, correct supply polarity and isolation. Have a qualified reviewer resolve the AC/inverter grounding/protection design.
3. **Individual acquisition tests:** vendor utilities/known fixtures first. Freeze radar firmware/profile and documented packet format; preserve raw output. Test camera and thermal formats independently. Establish RTK base/rover state semantics.
4. **Compute feasibility gate:** run a supported Hailo compiled vision model with selected UVC input, recording, radar/GNSS services and HMI together. Measure CPU/RAM, accelerator utilization, temperatures, p95/p99 source-to-display age and dropped samples. Target ≥10 RGB inference updates/s for the initial course is a requirement to evaluate, not an achieved FPS claim.
5. **Calibration:** coordinate axes/lever arms, RGB intrinsics, RGB–thermal and radar–body extrinsics, wheel circumference/track, time alignment, GNSS base coordinates and antenna references. Version every calibration.
6. **Stationary multi-sensor trials:** inert obstacles and warm targets; characterize empty-field/clutter behavior without treating no detection as a guarantee of clear space.
7. **Slow supervised motion:** empty controlled area first. Demonstrate wheel response and moving sensor geometry. Personnel safety remains independent of TARK.
8. **Cooperative course:** node B sends physical fixes while A receives them; demonstrate corridor and conflict evidence, then controlled loss/delay/correction degradation.
9. **Optical obscuration:** only venue-approved apparatus/fluids, trained supervision, ventilation and protected electronics. Stop if condensation, exposure concerns or loss of safe operator visibility arises. Prefer inert targets, not people inside aerosol.
10. **Replay and adversarial cases:** unplugged sensor, stale frame, wrong node/session, no-fix, wrong base reference, storage full, AP loss, restart and power loss. Record failures as well as successes.

Do not present a small artificial-aerosol chamber as a recreation of Bailadila monsoon microphysics. A visibility chart can support a measured contrast/recognition study; without calibrated extinction measurement it does not prove “3 m meteorological visibility.”

## 4. Calibration/test hardware allocation

F25 covers construction/access to a measured tape/grid, rigid ruler targets, printed optical calibration chart, safely edged radar reflector, stable warm reference object, marker stands and basic electrical/timing instruments. Borrow an oscilloscope/logic analyser and calibrated instruments where required. It does not buy a survey total station or calibrated blackbody. Use a qualified surveyed reference for absolute RTK error, otherwise report only relative consistency/repeatability and state the reference uncertainty.

The field course requires a site-approved layout with physical stand-off, independent spotters, brakes and barriers/markers. This is a laboratory test expense, not a paid mine trial. F26 is access/rental/consumables, not a claim that a suitable fog apparatus and venue are already secured.

## 5. Stopping-envelope and conflict reasoning boundaries

The hardware supports **shadow-mode evidence and advisory visualization**, not automatic vehicle authority. A stopping illustration may use:

`d_required = v * total_delay + v^2 / (2 * deceleration) + margin`

Deceleration must be positive and measured/justified for the modelled vehicle/load/grade; total delay includes sensing, processing, communication where used, operator/actuator response and uncertainty. If those values are absent, label the envelope PARAMETERIZED / NOT VALIDATED. Cart hand-braking is not a surrogate for a loaded dumper's brakes.

Radar Doppler is radial velocity. It is not automatically full relative velocity or closing speed along the drivable corridor. TTC only makes sense for the defined geometry and closing condition; crossing paths need occupancy analysis. Do not divide by zero for a stopped peer or turn an infinite/undefined TTC into an assurance of safety.

For cooperative junctions, project valid A/B poses onto a versioned road graph, retain map-match alternatives, expand occupied footprints by uncertainty and use predicted **intervals** of occupancy. A stopped vehicle already inside the conflict region continues to occupy it. A stale peer does not disappear into a “clear” state. Wrong datum/base coordinates can be more dangerous than no fix and require explicit checks.

Node B has no separately purchased IMU or dual-antenna heading system. Course derived from successive valid positions is usable only when displacement exceeds its uncertainty. At rest or during ambiguous motion, heading/intent remains unknown; neither a carried antenna nor a route assignment proves vehicle orientation. Record the cooperative node's actual footprint/role rather than labelling the carrier as a full dumper.

Navigation remains driver guidance, not autonomous steering. GNSS does not command motion. Optical confidence cannot override missing geometric evidence; thermal disagreement is retained rather than voted away. These are future integration requirements, not changes to current code in this task.

## 6. Industrial mapping

| Prototype element | Per-vehicle industrial function | Qualification/replacement needed |
|---|---|---|
| Pi/Hailo developer platform | Local deterministic acquisition, inference and evidence host | Rugged supported compute, EMC/thermal/vibration/power-failure design, maintenance and security lifecycle; architecture not locked to Pi |
| IWR6843ISK EVM | Forward obstacle geometry/radial motion | Qualified radar/product, authorized operating band, required range/coverage and documented interfaces; EVM not an operational safety sensor |
| B0200 | Semantic visible-light evidence | Rugged camera/optics, cleaning, glare/night/weather evaluation; stable time interface |
| Lepton/PT3 | Thermal corroboration | Appropriate resolution/lens, protective LWIR window, environmental and radiometric validation |
| GNSS rover | Vehicle position and time evidence | Suitable antenna, installation survey, corrections/coverage/integrity assessment; no GNSS-only lane authority |
| BNO085 and cart wheels | Body-motion plausibility | Vehicle-compatible IMU and OEM wheel/CAN/odometry input with isolation and semantics; wheel speed still not slip-free ground truth |
| Seven-inch panel/buzzer | Driver display and attention cue | Cab-readable/ergonomic HMI and acoustics, human-factors validation; no distraction-heavy interface |
| Wi-Fi AP and MCU peer | Cooperative communications | Surveyed coverage, secure identities, congestion/roaming/latency behavior; mine network technology selected separately |
| Power station/custom cart | Research energy and movement | **Not fitted to every dumper**; use qualified vehicle DC protection/conversion and approved mounts |
| Base/laptop/fixtures | Correction service, map/fleet/control room, calibration | Redundancy where needed, reference survey, backup/storage policy and trained operators |

## 7. Cost and N-vehicle scaling

Do not multiply INR 246,950 by fleet size. That number includes a cart, power station, test equipment/access and a second cooperative research node.

For industrial planning use:

`fleet_cost(N) = N * qualified_vehicle_kit_cost + base/correction_infrastructure + surveyed_RF_network + control_room_and_archive + survey/calibration + deployment_training + lifecycle_support`

The qualified vehicle-kit cost is **not priced by this student BOM**. Its sensors/enclosures/supply may be different and more expensive. A real mine may require multiple correction/RF sites, so shared does not mean one universal base/AP. Installation, cabling, survey, maintenance, cleaning and validation costs must be included.

Scaling telemetry to many vehicles should not upload every raw sensor stream continuously. Keep local incident buffers; send bounded health/position/intent/event summaries; retrieve evidence on demand. The server distributes relevant nearby participants rather than unrestricted all-to-all messages. Retain source-time uncertainty, message authentication and expiry through every relay.

Near-miss rate, availability, cycle-time effect and production impact are outcomes to measure against a controlled baseline. Do not claim percentages from the BOM. Better sensing cannot justify proceeding when the validated observable/stopping envelope is insufficient.

## 8. Open facts and release gates

| Gate | Unresolved fact / work | Consequence |
|---|---|---|
| G01 | Budget ceiling assumed from latest INR 250,000 record; exact quotations and tax treatment | Costed planning only; no order release |
| G02 | New cart CAD, material sections, brakes, wheels/axles, loaded mass and CG | No cutting list, load rating or mobile test release |
| G03 | Exact India-region EcoFlow unit/manual, inverter earthing topology, approved isolation/protective devices | No energization of the assembled distribution system |
| G04 | Radar delivered revision, approved firmware/profile, power demand and output schema | No claimed normalized acquisition or guaranteed range; higher-power mode not assumed |
| G05 | Permission/compliance for RF operation at the venue and country; EVM restrictions | No assumption that a module sale grants unrestricted operation |
| G06 | Exact Hailo runtime/model compatibility and combined-load timing | No measured inference/FPS/latency claim |
| G07 | Waveshare GNSS board UART levels, connector mapping, PPS availability, firmware/RTCM setup, supplied antenna specification | No final UART/PPS wiring or accuracy claim |
| G08 | New MCU revision, pin allocation, buffer/encoder carrier drawing and power limits | No final GPIO/header release; no old pin mapping reused |
| G09 | Thermal/raw formats, camera controls, timestamp alignment and shutter semantics | No radiometric or synchronized-fusion claim |
| G10 | USB hub revision/port current, display power/touch arrangement, enumeration and no-backfeed behavior | No simultaneous-load electrical release |
| G11 | Exact node-B battery/charger model, low-load behavior and runtime | Procurement spec only, no battery operating claim |
| G12 | Confirmed laboratory laptop/instrument access, outdoor course and approved obscuration facility | No hidden new-PC/survey-equipment purchase; revise budget if unavailable |
| G13 | Sensor calibration, error distributions, validated detectable domain and fault cases | No field safety, navigation integrity or mine-performance claim |
| G14 | Later software port/integration and regression work for this new BOM | Existing frozen code is not declared automatically compatible |

These are **new-design** gates. None depend on the old L298N, TT motor, unknown battery, HW678 photos or old GPIO investigation.

## 9. Exclusions and conclusion

Excluded from the flagship: the old hobby drivetrain/power/wiring; LD2450 as primary radar; automatic steering/braking; safety-rated E-stop claims; raw-ADC radar capture hardware; new premium sensors merely to spend reserve; a second full AI sensor vehicle; guaranteed GNSS under cover; independent absolute-position accuracy without reference; fake hardware telemetry; public-cloud motion authority; industrial certification or mine deployment under the student budget.

**Conclusion: a new, costed architecture recommendation is complete.** It is a credible two-participant, real-sensor, low-speed evidence and fleet-awareness research system when the integration gates are satisfied. It is **not fabrication-ready, commissioned, production-qualified or proof that a dumper can travel safely in 3–5 m visibility**. That distinction is part of the project's engineering strength, not an unfinished claim to conceal.

## 10. Document-level audit performed

- Six new Markdown documents checked; 27 unique BOM line IDs.
- Quantity × unit arithmetic checked independently for every cost row: no mismatches; base allocation INR 231,950.
- Reserve/headroom reconciled: INR 231,950 + INR 15,000 + INR 3,050 = INR 250,000.
- Relative document links checked for existing targets; none broken.
- Illustrative thermal storage, encoder count rate and runtime arithmetic independently recalculated. These remain calculations, not hardware measurements.
- SHA-256 comparison of all 71 pre-existing Master-1/Master-2 files: unchanged.
- Tracked Git source/staged diffs remained empty. No application source, firmware, existing schematic, software configuration or historical freeze document was edited.
- No software tests, device probes, physical experiments, purchases or supplier contacts were performed; none would verify this unbuilt architecture.
