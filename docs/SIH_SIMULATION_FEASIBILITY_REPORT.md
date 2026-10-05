# SIH SIMULATION FEASIBILITY REPORT

Analytical/sensitivity research only. Assumed inputs are not measured NMDC values. Physical validation pending; production R1 remains unchanged and traction remains DISABLED_PHASE_1.

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
