# 41 — PPT-ready engineering content

Revision M2-E1. Content only; no slide file has been edited. Every eventual diagram or screenshot must state its actual mode and maturity. Use only verified run evidence for result charts; otherwise label DESIGN or PROPOSED VALIDATION TARGET. Keep technical details in the linked appendix rather than shrinking slide text.

## Slide 1 — The problem is lost operating confidence, not only a poor image

**Diagram:** Mine road at a labelled problem-statement 3–5 m visibility condition; beside it show collision exposure and delayed haul cycles.

- Low visibility reduces awareness of obstacles, road alignment and other vehicles.
- SIH's supplied problem statement cites visibility as low as approximately 3–5 m; this is not our field measurement.
- Continuity is conditional on adequate evidence, not a promise to drive through every fog condition.

**Evidence:** [Design/source detail](01_COMPLETE_SYSTEM_ARCHITECTURE.md), [claim boundaries](36_CLAIM_MATRIX.md). The 3–5 m context is the supplied SIH statement, not a new external verification.

**Prohibited overclaim:** Do not present NMDC production or accident numbers as measured TARK results.

## Slide 2 — TARK turns observations into reasoned assistance

**Diagram:** Flowchart 1 in document 37; separate local decision path from monitoring.

- Acquire and validate sensor evidence before interpreting it.
- Combine route and fleet context without making the browser motion authority.
- Explain warnings, missing evidence and recovery through recorded reasons.
- Current software remains DISABLED_PHASE_1 with zero outputs.

**Evidence:** [Design/source detail](01_COMPLETE_SYSTEM_ARCHITECTURE.md), [claim boundaries](36_CLAIM_MATRIX.md). The 3–5 m context is the supplied SIH statement, not a new external verification.

**Prohibited overclaim:** Do not call the proposed R2 pipeline already implemented.

## Slide 3 — One frozen architecture, three physical GNSS roles

**Diagram:** Physical architecture in document 01: main Jetson vehicle, Pi rover B, base/control-room laptop.

- IWR1843BOOST + IMX291 B0200 + Lepton/PureThermal + BNO085 support complementary observations.
- Three LG290P kits serve rover A, rover B and local base.
- Two 14-bit SPI wheel paths support wheel response, not guaranteed ground speed.
- Keep exact wheel assembly and right motor GPIO release conditional on measurements.

**Evidence:** [Design/source detail](02_HARDWARE_ICD.md), [claim boundaries](36_CLAIM_MATRIX.md). The 3–5 m context is the supplied SIH statement, not a new external verification.

**Prohibited overclaim:** Do not label 100-degree diagonal RGB FOV as horizontal or claim regional SKU approval.

## Slide 4 — Evidence must be fresh, valid and interpretable

**Diagram:** Flowcharts 2–8, reduced to acquisition → health/time → tracks → association; show one unmatched target.

- Connected does not mean usable or characterized coverage.
- Radar supplies qualified geometry; RGB supplies semantics; thermal supplies contrast.
- Retain disagreement and unmatched evidence instead of forcing consensus.
- Every derived value carries provenance, timestamp, uncertainty and validity.

**Evidence:** [Design/source detail](07_EVIDENCE_AND_DATA_CONTRACT.md), [claim boundaries](36_CLAIM_MATRIX.md). The 3–5 m context is the supplied SIH statement, not a new external verification.

**Prohibited overclaim:** No-target does not mean clear road; thermal imagery does not supply independent range.

## Slide 5 — Mine navigation understands quality and restrictions

**Diagram:** Mine graph plus two candidate edges under uncertain localization.

- GNSS quality, IMU and qualified wheel aiding support the localization estimate.
- Use a versioned mine graph with closures, permitted directions and vehicle restrictions.
- Dijkstra selects allowed routes; ambiguous localization suppresses confident turn instructions.
- Fleet markers retain stale state instead of disappearing.

**Evidence:** [Design/source detail](15_DRIVER_NAVIGATION.md), [claim boundaries](36_CLAIM_MATRIX.md). The 3–5 m context is the supplied SIH statement, not a new external verification.

**Prohibited overclaim:** Do not call FIXED a guarantee of centimetre accuracy or claim autonomous steering.

## Slide 6 — Authority is bounded by evidence

**Diagram:** Flowcharts 15–18: supported distance → stopping inequality → state → endpoint, with independent cutoff branch.

- D_stop = v tau + v²/(2 a_eff) + M; no invented braking values.
- UNKNOWN is a visible condition, not a reassuring numeric default.
- Faults cannot increase capability; recovery requires restored evidence.
- V2 session and receiver expiry remain distinct from physical energy interruption.

**Evidence:** [Design/source detail](19_OPERATING_AUTHORITY_STATE_MACHINE.md), [claim boundaries](36_CLAIM_MATRIX.md). The 3–5 m context is the supplied SIH statement, not a new external verification.

**Prohibited overclaim:** Do not present supported speed as certified safe speed or a robot cutoff as HEMM braking.

## Slide 7 — Predict constrained-road conflict before direct sight

**Diagram:** Two rover trajectories entering one narrow section, with occupancy time intervals and uncertainty bands.

- Use route convergence, position/speed uncertainty and message age.
- Consider crossing, opposing, merging and stationary occupancy.
- Missing peers or corrections reduce confidence; they never establish clearance.
- Show conflict reason and evidence age, not a traffic-light permission to proceed.

**Evidence:** [Design/source detail](17_BLIND_CURVE_AND_JUNCTION_CONFLICT.md), [claim boundaries](36_CLAIM_MATRIX.md). The 3–5 m context is the supplied SIH statement, not a new external verification.

**Prohibited overclaim:** Do not claim detection of uninstrumented vehicles behind terrain from fleet telemetry.

## Slide 8 — Two interfaces, one truthful operational picture

**Diagram:** Driver wireframe on left and fleet/detail/replay views on right.

- Driver: state, supported/current speed, hazard, valid TTC and next maneuver.
- Control room: fleet, perception, incidents, replay, navigation, maintenance and analytics.
- Display REAL, SIMULATION or REPLAY on every relevant panel.
- No arbitrary direct-drive controls or hidden authority overrides.

**Evidence:** [Design/source detail](22_TARK_COMMAND_PLATFORM.md), [claim boundaries](36_CLAIM_MATRIX.md). The 3–5 m context is the supplied SIH statement, not a new external verification.

**Prohibited overclaim:** Do not show manufactured LIVE values or unsupported cycle-time metrics.

## Slide 9 — Validate each claim before showing it

**Diagram:** Gate staircase: device → stationary → separately authorized contained motion; parallel fixture/failure testing.

- Use repeatable clear-air/degraded/recovery runs and independent references.
- Perform controlled artificial-aerosol experiments, not a claimed mine-fog recreation.
- Measure misses, false alerts, uncertainty, warning latency and incident completeness.
- Current design review and future physical tests are separately labelled.

**Evidence:** [Design/source detail](29_KPIS_AND_ACCEPTANCE.md), [claim boundaries](36_CLAIM_MATRIX.md). The 3–5 m context is the supplied SIH statement, not a new external verification.

**Prohibited overclaim:** Do not show proposed targets as measured results or assign made-up pass rates.

## Slide 10 — Differentiate through traceable decisions

**Diagram:** Comparison rows: baseline sensing; TARK evidence/uncertainty, route-aware conflicts, degradation and replay.

- Use only competitor capabilities supported by Master‑1 evidence.
- Make uncertain and conflicting evidence inspectable.
- Demonstrate a failure and explain exactly why capability changes.
- Novelty is the coherent integration and evaluation, not proprietary claims over standard algorithms.

**Evidence:** [Design/source detail](30_NOVELTY_AND_DIFFERENTIATION.md), [claim boundaries](36_CLAIM_MATRIX.md). The 3–5 m context is the supplied SIH statement, not a new external verification.

**Prohibited overclaim:** No unsupported first-ever, only-team or guaranteed-superiority claims.

## Slide 11 — A research vehicle is a path to a retrofit—not a dumper controller

**Diagram:** Prototype-to-industrial mapping plus shadow → advisory → supervised pilot → approved intervention.

- Replace development packaging with qualified industrial integration through a later program.
- Use approved OEM/CAN/J1939 information and interfaces rather than connecting L298N concepts to real brakes.
- Plan site maps, maintenance, calibration, network coverage and human-factors evaluation.
- Intervention requires OEM/site and applicable safety approval beyond this prototype.

**Evidence:** [Design/source detail](34_INDUSTRIAL_DEPLOYMENT_MAPPING.md), [claim boundaries](36_CLAIM_MATRIX.md). The 3–5 m context is the supplied SIH statement, not a new external verification.

**Prohibited overclaim:** Do not imply mine certification, rugged ratings or approved brake authority.

## Slide 12 — A bounded budget with measurable impact hypotheses

**Diagram:** Budget bar: INR 192,150 electronics + INR 55,000 integration = INR 247,150; separate INR 2,850 reserve.

- The INR 250,000 ceiling and frozen Master‑1 selections are preserved.
- No extra premium sensors; regional procurement and delivery remain purchasing checks.
- Evaluate warning lead time, availability and incident explanation before industrial benefit claims.
- Production-loss reduction is a hypothesis for site trials, not a prototype percentage.

**Evidence:** [Design/source detail](33_IMPACT_AND_BENEFITS.md), [claim boundaries](36_CLAIM_MATRIX.md). The 3–5 m context is the supplied SIH statement, not a new external verification.

**Prohibited overclaim:** Do not reuse the historical INR 60,000 budget or imply this is industrial per-truck pricing.
