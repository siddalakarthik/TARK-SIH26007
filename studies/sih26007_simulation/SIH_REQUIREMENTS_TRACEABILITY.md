# SIH26007 requirements: source-locked research scope

Source review: 2026-09-29. Baseline: R1 `d385b055bef23af3b01960f7b2c113c2e683fe59`.
Official [SIH 2026 problem statements](https://sih.gov.in/sih2026PS), modal
`ViewProblemStatement26007`, retrieved directly with HTTP 200. Sponsor:
Ministry of Steel, department NMDC, category Hardware, theme Smart Automation.
The source archive and fingerprints are in `sources/`. Earlier failed web-tool
requests did not supply authority. Third-party mirrors and ChatGPT research PDFs
were excluded as requirement/numerical authorities.

## Explicit requirements and problem conditions

The following are concise paraphrases, not additional requirements invented by
the study. The archived modal preserves the original wording and section context.
The numerical condition is visual visibility, never a measured radar range.

| ID | Explicit condition or requested outcome | Official location | Study treatment |
|---|---|---|---|
| REQ-SIH-01 | Open-cast iron-ore mining, including Bailadila haul roads | Title; Background | Grade-neutral longitudinal model; no invented mine geometry |
| REQ-SIH-02 | Severe monsoon and dense fog impair visibility | Background | Condition transitions, without a sensor-physics transfer function |
| REQ-SIH-03 | Visual visibility can fall to approximately 3–5 metres | Background, haul-road visibility sentence | 3, 4 and 5 m visual-distance-constrained references |
| REQ-SIH-04 | Improve safe movement of HEMM, especially ore-transport dumpers | Background; Expected Outcomes | Stopping/perception requirements, not small-prototype scaling |
| REQ-SIH-05 | Address collision and road-accident risk | Problem Description; Expected Outcomes | Stationary, lead and oncoming longitudinal encounters |
| REQ-SIH-06 | Poor visibility forces slowing or temporary halts | Problem Description | Separate visual and parameterized halt references |
| REQ-SIH-07 | Increased haul-cycle times are a stated problem | Problem Description; Expected Outcomes | Normalized cycle-time comparison |
| REQ-SIH-08 | Fleet productivity, ore evacuation and production suffer | Problem Description | Normalized throughput only; no absolute production gains |
| REQ-SIH-09 | Maintain continuity of operations | Problem Description; Expected Outcomes | Availability, restriction and halt fractions |
| REQ-SIH-10 | Provide an intelligent, reliable, technology-driven solution | Problem Description | Monotonic degradation and scoped R1 communication evidence |
| REQ-SIH-11 | Enable movement that is both safe and efficient | Title; Problem Description | Maximize analytical speed subject to nonnegative model margin |
| REQ-SIH-12 | Improve operator awareness and assist guidance/collision avoidance | Expected Solution | Explainable encounter and integrated evidence; no steering claim |
| REQ-SIH-13 | Support real-time monitoring and operator/control-room decisions | Expected Solution; Expected Outcomes | Clear condition/fault timelines; no physical latency claim |
| REQ-SIH-14 | Support scalable deployment in large mechanized open-cast mines | Expected Outcomes | Full-scale perception requirements; deployment remains unvalidated |

Count: **14** explicit conditions/outcomes. REQ-SIH-12–14 retain relevant
requirements beyond the eleven candidates in the task. Numerical simulations
support only scoped engineering questions, not proof that every deployment
requirement is satisfied.

## Current official method and evaluation check

Reviewed the complete official [SIH 2026 guidelines](https://sih.gov.in/letters/2026/SIH%202026%20Guidelines.pdf)
(26 PDF pages), especially PDF page 20, and the official
[2026 idea template](https://sih.gov.in/letters/2026/SIH2026-IDEA-Presentation-Format.pptx)
(six submission slides plus an instruction slide).

**NO SPECIFIC SIMULATION TOOL/METHOD IS MANDATED BY THE OFFICIAL MATERIAL REVIEWED.**

No mandatory CARLA, Gazebo, ROS, Monte Carlo, MATLAB/Simulink, EKF, CFD, fog
chamber, specified fusion algorithm, chart list or simulation count was found.
The problem lists Digital Twin among optional technologies. Optional examples
are not compulsory methods. The ten simulations are this study's engineering
selection, not an SIH-prescribed checklist.

The 2026 guidelines actually reviewed include feasibility, practicability,
sustainability, impact, user experience, novelty, complexity, clarity and future
development in their evaluation criteria. The current template requests
technical approach, feasibility/viability, impact/benefits and references.
It limits submission to six slides including the title, submitted as PDF.
No 2025 rule has been silently relabelled 2026. The portal's older mobile links
are not authority for this review.

## Boundary

The statement supplies no calibrated braking, response delay, friction, grade,
haul-road length, cycle composition or trustworthy sensor range. Those inputs
will be labelled ASSUMED_SENSITIVITY, not official mine values. The source's
production-background quantities are not inputs to a forecast of production gain.
R1 software and electrical HOLDs remain unchanged. Physical validation is pending.
