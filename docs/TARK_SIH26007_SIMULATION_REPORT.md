# TARK SIH26007 SIMULATION REPORT

Analytical/sensitivity research only. Assumed inputs are not measured NMDC values. Physical validation pending; production R1 remains unchanged and traction remains DISABLED_PHASE_1.

## 1. Executive summary

| SIH Need | Simulation evidence | Primary metric | Actual result | Physical validation needed |
| --- | --- | --- | --- | --- |
| 3–5 m low visibility | SIM-01 | Reference cap at 3 / 4 / 5 m | 0 / 2.12204 / 3.87372 km/h | Perception/driver response/braking |
| Collision risk | SIM-03 | Stationary minimum clearance | 4.16667 m, own 5 m/s; 20 m detection | Geometry, brake response, moving targets |
| Safe movement | SIM-02 | Infeasible candidate points | 8845 grid points rejected at candidate speed | Loaded vehicle envelope |
| Efficient movement | SIM-08 | Reference cap at 40 m | 18 km/h, assumed desired limit | Achieved trustworthy range |
| Operational continuity | SIM-10 | Available condition-epoch fraction | 0.857143 | Dynamic recovery and vehicle response |
| Haul-cycle/productivity impact | SIM-08 | Reference throughput at 40 m | 1 baseline units | Actual cycle mix and downtime |
| Reliability | SIM-06 | Maximum live command | 0 across 66 recorded steps | Physical transport/watchdog/E-stop |
| Full-scale feasibility | SIM-09 | Reference range at 36 km/h | 51.3333 m | HEMM sensing, road/load/grade/braking |

All nonzero values use declared research assumptions, not measured mine performance.


## 2. Exact SIH26007 requirement extraction

| Requirement | Official condition/outcome | Studies | Evidence tables | Status / limitation |
| --- | --- | --- | --- | --- |
| REQ-SIH-01 | Open-cast setting | SIM-09 | sim09_fullscale_requirements.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-02 | Monsoon/fog | SIM-04, SIM-05, SIM-10 | sim04_fog_transition.csv; sim05_perception_degradation.csv; sim10_integrated.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-03 | 3–5 m visibility | SIM-01 | sim01_required_range_vs_speed.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-04 | HEMM safe movement | SIM-01, SIM-02, SIM-07, SIM-09 | sim01_required_range_vs_speed.csv; sim02_operating_envelope.csv; sim07_samples.csv; sim09_fullscale_requirements.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-05 | Collision risk | SIM-03, SIM-10 | sim03_encounters.csv; sim10_integrated.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-06 | Slow/stop operation | SIM-01, SIM-04, SIM-08 | sim01_required_range_vs_speed.csv; sim04_fog_transition.csv; sim08_operational_continuity.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-07 | Haul-cycle delay | SIM-08 | sim08_operational_continuity.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-08 | Productivity impact | SIM-08 | sim08_operational_continuity.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-09 | Continuity | SIM-04, SIM-08, SIM-10 | sim04_fog_transition.csv; sim08_operational_continuity.csv; sim10_integrated.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-10 | Reliability | SIM-05, SIM-06, SIM-07 | sim05_perception_degradation.csv; sim06_fault_story.csv; sim07_samples.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-11 | Safe and efficient movement | SIM-02, SIM-07 | sim02_operating_envelope.csv; sim07_samples.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-12 | Operator guidance | SIM-03, SIM-10 | sim03_encounters.csv; sim10_integrated.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-13 | Real-time monitoring | SIM-06, SIM-10 | sim06_fault_story.csv; sim10_integrated.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-14 | Scalability | SIM-09 | sim09_fullscale_requirements.csv | Scoped analytical support; physical outcome NOT VERIFIED |


## 3. Whether SIH mandates a specific simulator

No specific method/tool mandated by the reviewed official sources. See source-locked traceability document.

## 4. Simulation selection rationale

See `SIMULATION_SELECTION_MATRIX.md`: ten bounded engineering questions; no unrelated simulator added.

## 5. Source authority

Three archived official 2026 sources with URLs, dates and SHA-256 in sources/source_inventory.json. PS supplies visual 3–5 m, not physical sensor/braking performance. Exclude secondary AI-generated reports as numerical authority.

## 6. Parameter provenance

| Set | Delay s | Deceleration m/s² | Margin m | Reserve m |
| --- | --- | --- | --- | --- |
| favourable | 0.5 | 3.0 | 0.5 | 0.5 |
| reference | 1.5 | 1.5 | 2.0 | 1.0 |
| adverse | 2.5 | 0.5 | 5.0 | 5.0 |

All numeric controls are inventoried in inputs/parameter_registry.csv. The visual endpoints are OFFICIAL_SIH, 4 m DERIVED, freshness CURRENT_TARK_CONFIG, other physical values ASSUMED_SENSITIVITY.

## 7. Mathematical model

D_stop = v·t + v²/(2a) + m; R_required = D_stop + u; margin = R_trustworthy − R_required. Units: metres, seconds, m/s, m/s²; multiply m/s by 3.6 for km/h. Positive-root inverse gives maximum speed; if R ≤ m+u there is no positive admissible speed. Zero cap below reserves is NOT proof of feasibility. Age is added to response time in this research overlay; stale/missing/out-of-order evidence grants no positive capability. This overlay does not replace R1 production freshness, state transitions or hard cap.

## 8. Model assumptions

Constant effective deceleration and response, longitudinal point-gap geometry, no grade, brake buildup, tire/road model, sensing physics, lateral path planning, driver response distribution, measured sensor reliability, fleet dispatch or validated mine production inputs. Condition timelines are not dynamic vehicle trajectories. Operator/control-room outcomes are supported by explanations, not human-factors trials. Monte Carlo bounds are not empirical distributions. A finite-horizon oncoming result is not permanent collision avoidance. Hashes are content fingerprints, not digital signatures.

## 9. SIM-01 results

| Parameter set | Visual reference (m) | Model cap (m/s) | Model cap (km/h) | Margin at cap (m) |
| --- | --- | --- | --- | --- |
| favourable | 3.0 | 2.27492 | 8.1897 | 0 |
| favourable | 4.0 | 3 | 10.8 | 0 |
| favourable | 5.0 | 3.62348 | 13.0445 | 0 |
| reference | 3.0 | 0 | 0 | 0 |
| reference | 4.0 | 0.589454 | 2.12204 | 0 |
| reference | 5.0 | 1.07603 | 3.87372 | 0 |
| adverse | 3.0 | 0 | 0 | -7 |
| adverse | 4.0 | 0 | 0 | -6 |
| adverse | 5.0 | 0 | 0 | -5 |


## 10. SIM-02 results

27633 grid candidates; 8845 have negative model margin and are infeasible at their candidate speed. Cap is computed separately; no negative-margin optimization is permitted. See FIG-03 and full CSV.

## 11. SIM-03 results

| Encounter | Initial closing rate (m/s) | TTC research metric (s) | Minimum clearance (m) | Finite-horizon margin (m) | Modeled overlap |
| --- | --- | --- | --- | --- | --- |
| stationary | 5 | 8 | 4.16667 | 1.16667 | False |
| slower_lead | 2.5 | 16 | 14.1667 | 11.1667 | False |
| oncoming | 10 | 4 | -45 | -48 | True |

Reference case: own 5 m/s, initial separation 40 m, detection range 20 m; target speed stationary 0, lead 2.5, oncoming -5 m/s. Target never brakes. Horizon: own stop plus 5 s. Negative clearance denotes mathematical overlap, not post-impact physics. Oncoming vehicles continuing indefinitely eventually hit a stopped ego vehicle; finite-horizon clearance cannot establish permanent avoidance. Vehicle geometry is reduced to front-to-front clear gap, with no width, steering, grade, lateral trajectories or brake buildup.


## 12. SIM-04 results

Five independent condition epochs: visual range can fall while separately assumed trustworthy range remains unchanged; range loss and evidence loss reduce cap. See sim04_fog_transition.csv. No fog-to-radar transfer law is inferred.

## 13. SIM-05 results

Valid target, valid empty, missing and out-of-order evidence are separated. Empty space is not certified observable distance. Age consumes response budget and stale evidence halts analytical capability. Range contraction/uncertainty increase cannot increase cap. See sim05_perception_degradation.csv.

## 14. SIM-06 results

66 recorded steps across nine verified R1 scenarios EV-03,05,07,10,11,13,14,15,20. All projected live speed/left/right commands are zero; traction is DISABLED_PHASE_1. Freshness, communications, session, receiver reason and state are copied from the existing evidence. The analytical cap column is a separate research overlay, not production output. It is zero throughout these selected recorded conditions, so these traces demonstrate no positive-speed research benefit. Controlled logical time is not measured Pi/ESP32 latency. See `tables/sim06_fault_story.csv` and the R1 evidence manifest for original provenance.
| Trace | First sampled expiry (controlled s) | Max research cap (m/s) | Live command maximum | Recovery actions |
| --- | --- | --- | --- | --- |
| EV-03 | 1.1 | 0.0 | 0.0 | none |
| EV-05 | not observed | 0.0 | 0.0 | none |
| EV-07 | not observed | 0.0 | 0.0 | none |
| EV-10 | 0.7 | 0.0 | 0.0 | none |
| EV-11 | 0.7 | 0.0 | 0.0 | none |
| EV-13 | not observed | 0.0 | 0.0 | RESTART_RECEIVER; RESTART_SENDER |
| EV-14 | not observed | 0.0 | 0.0 | RESTART_SENDER; RESTORE_COMMUNICATION |
| EV-15 | not observed | 0.0 | 0.0 | TRANSPORT_RECONNECT |
| EV-20 | 2.3 | 0.0 | 0.0 | TRANSPORT_RECONNECT; RESTART_RECEIVER; RESTORE_COMMUNICATION |

Expiry threshold remains the existing Protocol V2 rule; sparse observation at 0.7 s is not a measured 0.7 s response guarantee. FIG-08 uses ordered steps with controlled-time labels so simultaneous events do not hide restart/recovery transitions.


## 15. SIM-07 results

| Samples | Minimum (m) | 5th (m) | Median (m) | 95th (m) | Maximum (m) | Negative fraction |
| --- | --- | --- | --- | --- | --- | --- |
| 1000 | -199.303 | -71.508 | 11.4303 | 73.4535 | 92.72 | 0.392 |
| 5000 | -224.987 | -74.4552 | 13.6462 | 74.6072 | 96.4305 | 0.3754 |
| 10000 | -224.987 | -73.3862 | 13.1554 | 74.2485 | 96.4305 | 0.3782 |
| 20000 | -232.568 | -74.0606 | 12.7168 | 74.796 | 96.4305 | 0.38235 |
| 40000 | -232.568 | -74.2404 | 12.3083 | 75.0084 | 96.4305 | 0.385725 |

Seed 26007; independent uniforms: delay 0.5–2.5 s, deceleration 0.5–3 m/s², reserve 0.5–5 m, trustworthy range 3–100 m, candidate speed 0–15 m/s; fixed margin 2 m. These distributions are study choices, not fitted mine distributions. Percentiles use linear interpolation. The final 20,000→40,000 prefix comparison passed the predeclared 0.02 fraction and 3 m percentile stability thresholds. This is a limited numerical stability diagnostic, not statistical confidence or distributional convergence proof. Largest absolute marginal Pearson correlation: speed_mps (-0.649097); dependent on the chosen bounds and not a universal importance ranking. Negative-margin fraction is NOT an accident probability.


## 16. SIM-08 results

| Set | Policy | Cycle-time index | Throughput index | Halt fraction |
| --- | --- | --- | --- | --- |
| favourable | visual_reference | 1.2 | 0.833333 | 0 |
| favourable | halt_reference | 1.25 | 0.8 | 0.2 |
| favourable | perception_concept | 1 | 1 | 0 |
| reference | visual_reference | 3.24473 | 0.308192 | 0 |
| reference | halt_reference | 1.25 | 0.8 | 0.2 |
| reference | perception_concept | 1 | 1 | 0 |
| adverse | visual_reference | 1.2934 | 0.773154 | 0.193289 |
| adverse | halt_reference | 1.2934 | 0.773154 | 0.193289 |
| adverse | perception_concept | 1.0434 | 0.958403 | 0 |

One clear-condition cycle = 1: fixed activities 0.4, nonfog travel 0.3, fog travel 0.3. Desired speed 5 m/s; constrained fog travel scales by desired/allowed speed. A halt adds a dwell index (0, 0.25 or 1) and then resumes at the cap for a separately assumed 40 m recovery envelope. Halt duration is not inferred from fog or sensors. The zero-dwell case is an instantaneous-recovery sensitivity bound, not a realistic guaranteed recovery. Nonfog travel is held constant and is not a vehicle-dynamics calculation. Throughput is 1/cycle, without tonnage or fleet scaling. At short range there may be no improvement; across dwell assumptions halting can outperform prolonged slow travel. Thus superiority is conditional, not universal.


## 17. SIM-09 results

| Set | Candidate speed (km/h) | Required range (m) | Max delay at 40 m (s) | Min deceleration at 40 m (m/s²) |
| --- | --- | --- | --- | --- |
| favourable | 7.2 | 2.66667 | 19.1667 | 0.0526316 |
| favourable | 18 | 7.66667 | 6.96667 | 0.342466 |
| favourable | 36 | 22.6667 | 2.23333 | 1.47059 |
| favourable | 54 | 46 | 0.1 | 3.57143 |
| reference | 7.2 | 7.33333 | 17.8333 | 0.0588235 |
| reference | 18 | 18.8333 | 5.73333 | 0.423729 |
| reference | 36 | 51.3333 | 0.366667 | 2.27273 |
| reference | 54 | 100.5 | INFEASIBLE | 7.75862 |
| adverse | 7.2 | 19 | 13 | 0.08 |
| adverse | 18 | 47.5 | 1 | 0.714286 |
| adverse | 36 | 135 | INFEASIBLE | 10 |
| adverse | 54 | 272.5 | INFEASIBLE | INFEASIBLE |

Requirements are grade-neutral sensitivity results. Effective deceleration, response, margin and uncertainty must be measured for vehicle load, road surface, slope, tire/brake state and deployment conditions. No friction coefficient, truck mass, mine geometry or regulatory stopping limit is invented. The simplified point model cannot establish full-scale compliance. LD2450 raw acquisition/decoder provenance limitations and all electrical HOLDs remain those of R1. No claimed radar immunity, thermal detection curve, IMU accuracy, GNSS availability or EKF fusion capability is added. A scaled prototype cannot validate HEMM sensing/braking distances.


## 18. SIM-10 results

| Epoch (s) | Condition | Visual (m) | Effective range (m) | Cap (km/h) | State | Link |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | low_visibility | 5 | 40 | 18 | MODEL_COMPATIBLE | True |
| 10 | dense_visual_fog | 3 | 40 | 18 | MODEL_COMPATIBLE | True |
| 20 | stopped_target | 3 | 20 | 18 | MODEL_COMPATIBLE | True |
| 30 | quality_degraded | 3 | 15 | 11.682 | RESTRICTED_MODEL | True |
| 40 | response_loss | 3 | 15 | 0 | HALT_UNAVAILABLE | False |
| 50 | session_and_evidence_recovered | 4 | 40 | 18 | MODEL_COMPATIBLE | True |
| 60 | restored | 5 | 40 | 18 | MODEL_COMPATIBLE | True |

Equal-duration condition assessment: available 0.857143, restricted 0.142857, halted 0.142857; normalized cap-time integral 0.807 versus visual reference 0.0783292. This is a continuity indicator, not actual distance or a physical speed trajectory. Cap changes are not instantaneous braking commands. Receiver expiry/session behavior comes from separate verified SIM-06 R1 traces, not from these synthetic booleans.


## 19. Safety–efficiency trade space

Within each fixed sensing/parameter case the positive-speed/remaining-margin curve is non-dominated: speed consumes margin. Different sensing resources are not free Pareto improvements. Optimization maximizes speed subject to nonnegative margin and declared bounds; never exchange negative margin for productivity.

## 20. Robustness / sensitivity

| Samples | Minimum (m) | 5th (m) | Median (m) | 95th (m) | Maximum (m) | Negative fraction |
| --- | --- | --- | --- | --- | --- | --- |
| 1000 | -199.303 | -71.508 | 11.4303 | 73.4535 | 92.72 | 0.392 |
| 5000 | -224.987 | -74.4552 | 13.6462 | 74.6072 | 96.4305 | 0.3754 |
| 10000 | -224.987 | -73.3862 | 13.1554 | 74.2485 | 96.4305 | 0.3782 |
| 20000 | -232.568 | -74.0606 | 12.7168 | 74.796 | 96.4305 | 0.38235 |
| 40000 | -232.568 | -74.2404 | 12.3083 | 75.0084 | 96.4305 | 0.385725 |

Seed 26007; independent uniforms: delay 0.5–2.5 s, deceleration 0.5–3 m/s², reserve 0.5–5 m, trustworthy range 3–100 m, candidate speed 0–15 m/s; fixed margin 2 m. These distributions are study choices, not fitted mine distributions. Percentiles use linear interpolation. The final 20,000→40,000 prefix comparison passed the predeclared 0.02 fraction and 3 m percentile stability thresholds. This is a limited numerical stability diagnostic, not statistical confidence or distributional convergence proof. Largest absolute marginal Pearson correlation: speed_mps (-0.649097); dependent on the chosen bounds and not a universal importance ranking. Negative-margin fraction is NOT an accident probability.


## 21. Operational continuity

| Set | Policy | Cycle-time index | Throughput index | Halt fraction |
| --- | --- | --- | --- | --- |
| favourable | visual_reference | 1.2 | 0.833333 | 0 |
| favourable | halt_reference | 1.25 | 0.8 | 0.2 |
| favourable | perception_concept | 1 | 1 | 0 |
| reference | visual_reference | 3.24473 | 0.308192 | 0 |
| reference | halt_reference | 1.25 | 0.8 | 0.2 |
| reference | perception_concept | 1 | 1 | 0 |
| adverse | visual_reference | 1.2934 | 0.773154 | 0.193289 |
| adverse | halt_reference | 1.2934 | 0.773154 | 0.193289 |
| adverse | perception_concept | 1.0434 | 0.958403 | 0 |

One clear-condition cycle = 1: fixed activities 0.4, nonfog travel 0.3, fog travel 0.3. Desired speed 5 m/s; constrained fog travel scales by desired/allowed speed. A halt adds a dwell index (0, 0.25 or 1) and then resumes at the cap for a separately assumed 40 m recovery envelope. Halt duration is not inferred from fog or sensors. The zero-dwell case is an instantaneous-recovery sensitivity bound, not a realistic guaranteed recovery. Nonfog travel is held constant and is not a vehicle-dynamics calculation. Throughput is 1/cycle, without tonnage or fleet scaling. At short range there may be no improvement; across dwell assumptions halting can outperform prolonged slow travel. Thus superiority is conditional, not universal.


## 22. Full-scale HEMM requirements

| Set | Candidate speed (km/h) | Required range (m) | Max delay at 40 m (s) | Min deceleration at 40 m (m/s²) |
| --- | --- | --- | --- | --- |
| favourable | 7.2 | 2.66667 | 19.1667 | 0.0526316 |
| favourable | 18 | 7.66667 | 6.96667 | 0.342466 |
| favourable | 36 | 22.6667 | 2.23333 | 1.47059 |
| favourable | 54 | 46 | 0.1 | 3.57143 |
| reference | 7.2 | 7.33333 | 17.8333 | 0.0588235 |
| reference | 18 | 18.8333 | 5.73333 | 0.423729 |
| reference | 36 | 51.3333 | 0.366667 | 2.27273 |
| reference | 54 | 100.5 | INFEASIBLE | 7.75862 |
| adverse | 7.2 | 19 | 13 | 0.08 |
| adverse | 18 | 47.5 | 1 | 0.714286 |
| adverse | 36 | 135 | INFEASIBLE | 10 |
| adverse | 54 | 272.5 | INFEASIBLE | INFEASIBLE |


## 23. Most important numerical findings

| Finding | Value | Conditions | Meaning | Does not prove |
| --- | --- | --- | --- | --- |
| 4 m visual reference | 2.12204 km/h | {"parameter_set": "reference", "trustworthy_perception_range_m": 4} | Small visual range severely constrains this model | A calibrated driver speed recommendation |
| 5 m visual reference | 3.87372 km/h | {"parameter_set": "reference", "trustworthy_perception_range_m": 5} | Model upper speed bound at 5 m | Radar range in fog |
| 18 km/h perception requirement | 18.8333 m | {"parameter_set": "reference", "speed_mps": 5, "trustworthy_perception_range_m": 40} | Required distance under declared reference parameters | Current hardware can perceive that far reliably |
| 36 km/h perception requirement | 51.3333 m | {"parameter_set": "reference", "speed_mps": 10, "trustworthy_perception_range_m": 40} | Quadratic braking cost matters | Full-scale truck validation |
| Stationary target clearance | 4.16667 m | {"parameter_set": "reference", "initial_separation_m": 40, "trustworthy_perception_range_m": 20, "speed_mps": 5, "encounter_type": "stationary"} | Point clearance after delayed detection and braking | Collision avoidance in arbitrary roads |
| 40 m concept cycle | 1 baseline-cycle units | {"parameter_set": "reference", "range_case_m": 40, "dwell_index": 0.25, "policy": "perception_concept"} | No added fog travel delay in this assumed case | A measured haul-cycle saving |
| 4 m visual throughput | 0.308192 baseline-throughput units | {"parameter_set": "reference", "range_case_m": 40, "dwell_index": 0.25, "policy": "visual_reference"} | Normalized travel restriction cost | Actual ore evacuation or MTPA impact |
| Uncertainty negative-margin share | 0.385725 fraction of engineering samples | {"samples": 40000} | Fraction of assumed candidate points failing the model constraint | Accident probability or reliability |


## 24. SIH requirement-to-result matrix

| Requirement | Official condition/outcome | Studies | Evidence tables | Status / limitation |
| --- | --- | --- | --- | --- |
| REQ-SIH-01 | Open-cast setting | SIM-09 | sim09_fullscale_requirements.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-02 | Monsoon/fog | SIM-04, SIM-05, SIM-10 | sim04_fog_transition.csv; sim05_perception_degradation.csv; sim10_integrated.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-03 | 3–5 m visibility | SIM-01 | sim01_required_range_vs_speed.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-04 | HEMM safe movement | SIM-01, SIM-02, SIM-07, SIM-09 | sim01_required_range_vs_speed.csv; sim02_operating_envelope.csv; sim07_samples.csv; sim09_fullscale_requirements.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-05 | Collision risk | SIM-03, SIM-10 | sim03_encounters.csv; sim10_integrated.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-06 | Slow/stop operation | SIM-01, SIM-04, SIM-08 | sim01_required_range_vs_speed.csv; sim04_fog_transition.csv; sim08_operational_continuity.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-07 | Haul-cycle delay | SIM-08 | sim08_operational_continuity.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-08 | Productivity impact | SIM-08 | sim08_operational_continuity.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-09 | Continuity | SIM-04, SIM-08, SIM-10 | sim04_fog_transition.csv; sim08_operational_continuity.csv; sim10_integrated.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-10 | Reliability | SIM-05, SIM-06, SIM-07 | sim05_perception_degradation.csv; sim06_fault_story.csv; sim07_samples.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-11 | Safe and efficient movement | SIM-02, SIM-07 | sim02_operating_envelope.csv; sim07_samples.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-12 | Operator guidance | SIM-03, SIM-10 | sim03_encounters.csv; sim10_integrated.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-13 | Real-time monitoring | SIM-06, SIM-10 | sim06_fault_story.csv; sim10_integrated.csv | Scoped analytical support; physical outcome NOT VERIFIED |
| REQ-SIH-14 | Scalability | SIM-09 | sim09_fullscale_requirements.csv | Scoped analytical support; physical outcome NOT VERIFIED |


## 25. Comparison to current R1 production maturity

The production R1 pipeline uses stopping-distance algebra, tracked envelope/uncertainty and explicit maturity gates, with hard_cap_mps = 0. This independent study reuses the dimensional stopping principle but inverts it for research and adds encounter/normalized-cycle calculations. Study reference parameters are NOT production configuration. SIM-06 copies existing verified R1 traces; all other nonzero speed values are analytical, never commands. Archived simulations 1/2/3 were examined for lineage only; their outputs are not reused as verified numbers. No archived EKF result is credited to production.

## 26. Limitations

Constant effective deceleration and response, longitudinal point-gap geometry, no grade, brake buildup, tire/road model, sensing physics, lateral path planning, driver response distribution, measured sensor reliability, fleet dispatch or validated mine production inputs. Condition timelines are not dynamic vehicle trajectories. Operator/control-room outcomes are supported by explanations, not human-factors trials. Monte Carlo bounds are not empirical distributions. A finite-horizon oncoming result is not permanent collision avoidance. Hashes are content fingerprints, not digital signatures.

## 27. Physical validation still required

Keep all controlled electrical HOLDs. Verify purchased sensors/protocol/identity, wiring/voltage, calibrated range and freshness, loaded truck response/deceleration under grade/surface/weather, physical E-stop/watchdog, driver HMI and supervised site trials. This study makes no physical verification claim.

## 28. Reproduction instructions

From repo: `python -m pip install -r studies/sih26007_simulation/requirements.txt` into a separate study environment; `python -B studies/sih26007_simulation/run_all.py`; then `python -B studies/sih26007_simulation/run_all.py --verify`. See study README for production regression commands. No hardware required.

## 29. Artifact inventory

- `sim01_safe_speed_vs_range.png` / `.svg` ← `tables/sim01_safe_speed_vs_range.csv`
- `sim01_required_range_vs_speed.png` / `.svg` ← `tables/sim01_required_range_vs_speed.csv`
- `sim01_visual_reference.png` / `.svg` ← `tables/sim01_safe_speed_vs_range.csv`
- `sim01_stopping_components.png` / `.svg` ← `tables/sim01_safe_speed_vs_range.csv`
- `sim02_safety_efficiency_map.png` / `.svg` ← `tables/sim02_operating_envelope.csv`
- `sim02_speed_cap_curves.png` / `.svg` ← `tables/sim01_safe_speed_vs_range.csv`
- `sim03_clearance_map.png` / `.svg` ← `tables/sim03_encounters.csv`
- `sim03_closing_scenarios.png` / `.svg` ← `tables/sim03_encounters.csv`
- `sim03_required_detection_range.png` / `.svg` ← `tables/sim03_encounters.csv`
- `sim04_fog_timeline.png` / `.svg` ← `tables/sim04_fog_transition.csv`
- `sim10_integrated.png` / `.svg` ← `tables/sim10_integrated.csv`
- `sim04_envelope_contraction.png` / `.svg` ← `tables/sim04_fog_transition.csv`
- `sim10_health_timeline.png` / `.svg` ← `tables/sim10_integrated.csv`
- `sim05_uncertainty_sensitivity.png` / `.svg` ← `tables/sim05_perception_degradation.csv`
- `sim05_range_degradation.png` / `.svg` ← `tables/sim05_perception_degradation.csv`
- `sim06_fault_timeline.png` / `.svg` ← `tables/sim06_fault_story.csv`
- `sim07_margin_distribution.png` / `.svg` ← `tables/sim07_samples.csv`
- `sim07_parameter_sensitivity.png` / `.svg` ← `tables/sim07_sensitivity.csv`
- `sim07_convergence.png` / `.svg` ← `tables/sim07_uncertainty_samples_summary.csv`
- `sim08_cycle_time_comparison.png` / `.svg` ← `tables/sim08_operational_continuity.csv`
- `sim08_productivity_retention.png` / `.svg` ← `tables/sim08_operational_continuity.csv`
- `sim08_halt_fraction.png` / `.svg` ← `tables/sim08_operational_continuity.csv`
- `sim09_required_perception_range.png` / `.svg` ← `tables/sim09_fullscale_requirements.csv`
- `sim09_requirement_feasibility_map.png` / `.svg` ← `tables/sim09_fullscale_requirements.csv`
- `safety_efficiency_trade_space.png` / `.svg` ← `tables/safety_efficiency_trade_space.csv`

CSV/JSON/config/source/report/figure hashes: hashes.json; provenance/environment: manifest.json. Source PDFs/PPTX are retained as evidence, not edited.

## 30. Submission-ready conclusions

The study quantifies conditional requirements and limitations, not achieved hardware performance. Show the 3–5 m restriction, full-scale range requirement and normalized cycle result with assumptions beside each. Ready status additionally requires recorded R1 regression and visual QA gates; consult reports/QUALITY_GATE.md.
