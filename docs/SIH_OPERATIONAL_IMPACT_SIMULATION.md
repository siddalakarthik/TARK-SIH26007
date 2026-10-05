# SIH OPERATIONAL IMPACT SIMULATION

Analytical/sensitivity research only. Assumed inputs are not measured NMDC values. Physical validation pending; production R1 remains unchanged and traction remains DISABLED_PHASE_1.

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

## Integrated condition-epoch continuity

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
