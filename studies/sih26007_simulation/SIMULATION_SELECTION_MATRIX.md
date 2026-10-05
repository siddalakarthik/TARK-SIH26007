# Requirement-driven selection (before execution)

| Study | Engineering question | Requirements | Method / reason | Excluded claim |
|---|---|---|---|---|
| SIM-01 | What stopping range and speed fit 3/4/5 m? | 03,04,06 | Constant-deceleration algebra and independent root solver | Calibrated truck stopping |
| SIM-02 | Where is nonnegative margin possible? | 04,11 | Exhaustive declared range/speed grid | Certified safe operating envelope |
| SIM-03 | How do stationary, lead and oncoming encounters differ? | 05,12 | Exact piecewise relative motion | Lateral avoidance or opponent cooperation |
| SIM-04 | What happens as conditions contract/recover? | 02,06,09 | Synthetic condition epochs | Instantaneous vehicle deceleration |
| SIM-05 | Can degradation ever increase capability? | 02,10,11 | Range, age, uncertainty and report-kind sweeps | Fog-to-radar performance law |
| SIM-06 | How does authority fail closed in R1? | 10,13 | Project existing verified production-path traces | Physical watchdog or latency |
| SIM-07 | How sensitive are conclusions to assumed inputs? | 04,10,11 | Seeded independent uniform sampling and prefix stability | Accident probability |
| SIM-08 | What normalized continuity benefit is possible? | 06,07,08,09 | Three-policy normalized cycle model with dwell sweep | Mine production gain |
| SIM-09 | What capability would full-scale operation require? | 01,04,14 | Invert response, braking and perception constraints | Prototype meets those requirements |
| SIM-10 | Can the scenario be explained end to end? | 02,05,09,12,13 | Condition timeline plus separate R1 authority evidence | Simulated physical command execution |

REQ-SIH prefixes are omitted for compactness. All 14 extracted conditions/outcomes
are addressed as engineering questions, not asserted satisfied in the field.
Pareto analysis stays within each fixed sensing/parameter case. It never trades
negative margin for throughput. No CARLA, EKF, CFD or digital-twin work is added:
none is needed to answer these bounded questions or mandated by reviewed sources.
