# TARK R2 — Complete Engineering Blueprint 2

HISTORICAL / SUPERSEDED design branch. The current R3 software status is in
`docs/R3_REASONING_REPORT.md`; see `docs/TARK_RELEASE_INDEX.md` before using
earlier equipment, power or control diagrams. Not an as-built wiring release.

Revision M2-E1 • Completed 2 October 2026 • SIH26007 / NMDC context

**MASTER ENGINEERING BLUEPRINT 2: PASSED — DESIGN SCOPE ONLY.**

This is the consolidated Master‑2 entry point. Master‑1 remains authoritative for hardware selection. This complete 47-document package expands the earlier short handoff under `docs/tark-r2-master/master-2/`, which is preserved as historical context rather than silently overwritten. Owning detailed documents are linked beneath each section. No hardware, application code, firmware, purchases or PPT files were modified in this design task.

## 1. Executive technical summary

TARK R2 is a research-demonstrator design for evidence-qualified driver assistance, localization, mine-route guidance and cooperative risk awareness in low visibility. The main vehicle acquires local radar/RGB/thermal/IMU/GNSS observations, keeps their limitations explicit, and derives reasoned operating constraints. A separate endpoint supervises bounded requests; a separate physical cutoff interrupts prototype traction energy. Node B and the base/control-room computer add cooperative context and replayable monitoring, never browser motion authority.

**Detailed design:** [Executive technical summary](01_COMPLETE_SYSTEM_ARCHITECTURE.md).

## 2. Problem interpretation

The supplied SIH26007 statement describes visibility potentially falling to approximately 3–5 m and consequent collision risk, lost haulage efficiency and interruptions. This is problem context, not our measurement. TARK addresses awareness and decision support while recognizing that insufficient evidence may require restriction or stopping; it does not promise uninterrupted operation in every fog condition.

**Detailed design:** [Problem interpretation](33_IMPACT_AND_BENEFITS.md).

## 3. Design philosophy

Evidence must carry source, time, validity, quality, uncertainty and calibration identity. No-target is not free space, network silence is not road clearance, and named object confidence is not a braking guarantee. Failures can remove capabilities, never silently increase them. Keep REAL, SIMULATION and REPLAY visibly separate; preserve R1 and build R2 through controlled adapters and gates.

**Detailed design:** [Design philosophy](07_EVIDENCE_AND_DATA_CONTRACT.md).

## 4. Master‑1 hardware freeze

Retain the Orin Nano Super 8 GB platform, IWR1843BOOST, Arducam B0200 IMX291, Lepton 3.5 500-0771-01 with PURETHERMAL‑3, Adafruit 4754 BNO085 over SPI, three Waveshare 33000 LG290P kits, two 14-bit SPI wheel paths, owned ESP32-S3 and Pi 3B+, Waveshare 11199 HMI, Kingston SNV3S/500G, UH720 V5, TL-WR902AC V3 and Grove 107020000. Retain the L298N/four-TT/acrylic demonstrator subject to load qualification. Wheel carrier/magnet geometry, right-channel GPIO16/17 and Jetson regional purchasing SKU are the explicit handoff holds—not invitations to reselect sensors.

**Detailed design:** [Master‑1 hardware freeze](../tark-r2-master/03_EXACT_COMPONENT_FREEZE.md).

## 5. Complete system architecture

Vehicle A hosts Jetson perception/decision support and ESP32 local supervision. Vehicle B is the Pi-hosted GNSS cooperative node, not another perception computer. The existing laptop hosts the base receiver owner, correction distribution, fleet relay and control-room services. Local sensing and endpoint expiry do not depend on that laptop or a browser. Industrial integration is a separate mapping, not an additional purchased node.

**Detailed design:** [Complete system architecture](01_COMPLETE_SYSTEM_ARCHITECTURE.md).

## 6. Electrical architecture

The logical ICD defines device hosts, directions, references, power roles and release conditions. Jetson U1/U2/U3 serve radar/RGB/ESP32; U4 serves the powered hub. Hub data ports serve thermal, rover A and qualified touch/power; charging-only ports are not data ports. Jetson SPI serves IMU; ESP32 SPI serves wheel paths. The display uses DP-to-HDMI plus separate qualified touch/power. These allocations do not invent PCB header numbers or final motor GPIOs.

**Detailed design:** [Electrical architecture](02_HARDWARE_ICD.md).

## 7. Mechanical architecture

Use a measured body frame x forward, y left, z up. Place sensors to preserve overlap, antenna view and cooling while separating motor/noisy power harnesses. Define mounts using measured chassis/payload/connector envelopes, not invented dimensions. Wheel assemblies require coaxial alignment and documented magnetic geometry. The acrylic model cannot be treated as a scaled dumper dynamic model.

**Detailed design:** [Mechanical architecture](05_MECHANICAL_LAYOUT.md).

## 8. Sensor geometry

Calibrate RGB intrinsics and cross-sensor extrinsics; transform radar, camera, thermal, IMU and GNSS lever arms to the body frame. The camera's 100-degree specification is diagonal; actual useful HFOV/near focus is measured. Thermal has its own native geometry and does not gain radar range without valid association. Record remount repeatability, calibration/software/hardware identity and validity.

**Detailed design:** [Sensor geometry](06_SENSOR_GEOMETRY_AND_CALIBRATION.md).

## 9. Power

Separate traction from qualified electronics branches. The electronics category uses a protected LiFePO4 source with matched charging and regulated 19 V compute, 12 V hub and suitable 5 V/3.3 V branches; exact pack/converter/fuse/wire choices await measured loads. Do not assume converter negatives are isolated or common. Never power Pi/Jetson/ESP32 from L298N 5 V; never reuse the burnt LM2596. A rated manual DC disconnect in the sole traction feed is independent of Jetson/Wi-Fi/browser and is not a certified E-stop.

**Detailed design:** [Power](04_POWER_ARCHITECTURE.md).

## 10. Evidence model

ObservationEnvelope contains source epoch/sequence, sensor/reception/processing timestamps, clock-domain mapping with uncertainty, mode, calibration, frame, validity/quality, uncertainty and bounded payload. CONNECTED, FRESH, VALID, USABLE and COVERAGE_CHARACTERIZED are different. Native and remote clocks cannot be compared as if they share an epoch; unbounded time uncertainty invalidates dependent fusion/prediction.

**Detailed design:** [Evidence model](07_EVIDENCE_AND_DATA_CONTRACT.md).

## 11. Radar

Pin the TI processed-data firmware/profile/packet contract and validate it before normalization. Proposed range-aware DBSCAN plus Kalman tracking, Mahalanobis gates and assignment produces persistent objects and uncertainty; sparse relevant returns remain explicit. Radial velocity is not full planar velocity. Range, useful coverage and detectability require target/environment-specific characterization rather than datasheet maximum extrapolation.

**Detailed design:** [Radar](08_RADAR_PERCEPTION.md).

## 12. RGB

Acquire truthful timestamped UVC frames and detect dropouts/frozen data. Use image quality indicators without claiming visibility metres. YOLO11n is a candidate edge benchmark, compared against the documented alternatives at pinned input/mode/license; inference performance is not yet measured. Visual classes remain separate from geometry and can be unsupported in degraded imagery.

**Detailed design:** [RGB](09_RGB_PERCEPTION.md).

## 13. Thermal

Acquire Lepton through PT3, preserving native frame timing, FFC/shutter state and actual mode. Initial processing identifies contrast regions and temporal support rather than inventing independent range. Pseudo-colour, thermal intensity and radiometric temperature are distinct; any temperature interpretation depends on the documented delivered configuration.

**Detailed design:** [Thermal](10_THERMAL_PERCEPTION.md).

## 14. IMU

The frozen BNO085 uses its documented SPI/interrupt/reset interface at compatible logic levels. Normalize orientation/angular-motion reports with validity and mounting alignment; preserve calibration status. Use qualified yaw-rate aiding in the estimator, not long-term position by double integration or unquestioned magnetic heading beside motors and steel. Existing BNO055 code is not automatically a BNO085 implementation.

**Detailed design:** [IMU](13_LOCALIZATION_ENGINE.md).

## 15. Wheel motion

Two magnetic-angle paths feed the endpoint; 14-bit resolution is 16384 codes/revolution, not an accuracy guarantee. Signed unwrap requires a bounded sample gap and less than half-turn motion between usable samples. Radius/sign/time calibration converts angular change into wheel response; slip/turning/missing data remain explicit. Current V2 STATUS cannot silently carry the proposed wheel payload.

**Detailed design:** [Wheel motion](12_VEHICLE_MOTION_MODEL.md).

## 16. Tracking

Use a bounded constant-velocity state with prediction/covariance propagation and assignment, explicit tentative/confirmed/coasting lifecycle and source support. Slot number is not persistent physical identity. Assess identity switches, fragmented tracks, missed targets and false tracks with independent annotated runs; cap work/queues and record dropped observations rather than accumulating delay.

**Detailed design:** [Tracking](08_RADAR_PERCEPTION.md).

## 17. Fusion

Associate only after frame calibration, timing and uncertainty checks. Keep matched, unmatched and disagreeing evidence visible. A radar obstacle without RGB support remains a geometric obstacle; a visual truck without range has no fabricated distance/TTC. Correlated inputs cannot be treated as independent confirmations that arbitrarily shrink covariance.

**Detailed design:** [Fusion](11_MULTISENSOR_FUSION.md).

## 18. Localization

A limited planar EKF combines qualified GNSS, gyro and wheel aiding with explicit uncertainty, lever arms and base/datum identity. Report native solution quality such as SINGLE/FLOAT/FIXED and stale/invalid states. Map matching retains competing edge hypotheses and cannot cosmetically improve uncertain GNSS. No long-term GNSS-free inertial or guaranteed RTK accuracy claim is made.

**Detailed design:** [Localization](13_LOCALIZATION_ENGINE.md).

## 19. Mine map

Use a versioned mine road graph with nodes for junctions, operating points, narrow sections and hazards; edges carry direction, vehicle permissions, closures, restrictions and known geometry. Unknown grade/width is not zero. Synthetic demonstration maps are labelled; real mine roads and coordinate datum need authorized/reference evidence. Keep geographic locations separate from radar-local coordinates.

**Detailed design:** [Mine map](14_MINE_NAVIGATION_GRAPH.md).

## 20. Route planning

Use Dijkstra on validated nonnegative costs after exclusion of prohibited/closed edges. Generate maneuvers only from sufficiently unambiguous localization and valid map context; otherwise display position uncertainty or route unavailable. A route is guidance, not local clearance, steering or permission to exceed supported operating limits.

**Detailed design:** [Route planning](15_DRIVER_NAVIGATION.md).

## 21. Fleet telemetry

Authenticated local Wi-Fi messages carry node/epoch/sequence, time/quality, pose, motion, route, state and health through a bounded laptop relay. Each physical GNSS receiver has one owner for its documented data/correction interface. Initial update/age thresholds are fixture targets, not measured radio performance. Missing nodes retain visibly stale last-known evidence; peer loss cannot mean no vehicle.

**Detailed design:** [Fleet telemetry](16_FLEET_TELEMETRY_AND_V2X.md).

## 22. Blind-curve prediction

Compare plausible route occupancy intervals including footprint, localization/speed/time uncertainty, map geometry and telemetry age. Cover opposing narrow-road traffic, crossing, merge and stationary occupancy; zero lower speed may mean no finite exit time. UNKNOWN/POTENTIAL_CONFLICT/HIGH_CONFLICT/NO_CONFLICT are evidence assessments, not right-of-way control. NO_CONFLICT applies only to supported hypotheses.

**Detailed design:** [Blind-curve prediction](17_BLIND_CURVE_AND_JUNCTION_CONFLICT.md).

## 23. TTC / CPA

For qualified radial closing geometry TTC=r/(-r_dot); otherwise return NON_CLOSING, INVALID or UNKNOWN rather than an invented number. Crossing risk uses t_CPA=−(p·v)/(v·v), valid horizon and closest separation with footprint/uncertainty. Radial-only velocity is insufficient to claim a full crossing trajectory. All calculations use one stated relative frame and valid timing.

**Detailed design:** [TTC / CPA](08_RADAR_PERCEPTION.md).

## 24. Stopping model

D_stop=v tau+v²/(2 a_eff)+M for qualified nonnegative speed, positive effective deceleration, delay allowance and uncertainty margin. Robot deceleration/coasting must be characterized separately from HEMM braking. Industrial parameters depend on OEM, load, tyres, surface, grade and weather; none is invented here.

**Detailed design:** [Stopping model](18_STOPPING_AND_SAFE_OPERATING_ENVELOPE.md).

## 25. Safe operating envelope

For qualified D=D_usable−M≥0, invert the stopping inequality to v_max=sqrt((a tau)²+2aD)−a tau, with numerically stable alternative and explicit zero case. Usable distance depends on characterized coverage and relevant obstacle/route limits, not the lack of a return. Unknown required inputs mean no reassuring positive speed. This is a shadow design model; current Phase‑1 output and permitted motion remain zero.

**Detailed design:** [Safe operating envelope](18_STOPPING_AND_SAFE_OPERATING_ENVELOPE.md).

## 26. Operating authority

Retain NORMAL, WARN, RESTRICT, STOP and UNKNOWN with deterministic conditions/reasons, capability intersections, immediate escalation and qualified recovery. A known stop cause remains latched despite a separate unknown condition. Proposed freshness/dwell thresholds are versioned test parameters, not measured mine-safety constants. No browser, fleet message or reconnect grants unrestricted authority.

**Detailed design:** [Operating authority](19_OPERATING_AUTHORITY_STATE_MACHINE.md).

## 27. ESP32 endpoint

Reuse the single existing Protocol V2 framing/codec/supervisor: bounded COBS, CRC32C, canonical CBOR, sessions/sequences, request checks and ACK/NACK/STATUS. Current zero-output behavior is unchanged. Future physical USB/serial, boot identity, tick and watchdog binding require exact board evidence. Receipt-based lifetime is not an end-to-end age proof. Wheel feedback and any positive-authority age revision require coordinated host/firmware/shared-vector review, not undeclared fields.

**Detailed design:** [ESP32 endpoint](20_LOCAL_ENDPOINT_ARCHITECTURE.md).

## 28. Driver HMI

Show state, supported/current speed with validity, nearest hazard and qualified distance/TTC, next maneuver/current road/destination, GNSS quality and critical health. Prioritize glanceable text/symbol/colour, not colour alone. Audible alerts support but do not replace visual information. Every panel states mode, unavailable data stays unavailable and engineering diagnostics do not overwhelm the driver.

**Detailed design:** [Driver HMI](21_DRIVER_HMI.md).

## 29. Control-room platform

Extend existing React/TypeScript/MapLibre and FastAPI/WebSocket conventions rather than create a second app. Specify fleet command centre, vehicle detail, perception, incidents, replay, mine navigation, analytics, maintenance/calibration and administration. Roles may inspect or publish approved audited context, not directly drive motors or override local limits. Industrial PostgreSQL/PostGIS/MQTT-style scaling is a later deployment path.

**Detailed design:** [Control-room platform](22_TARK_COMMAND_PLATFORM.md).

## 30. Replay

Record normalized inputs, decisions/reasons, health, configurations, calibration, endpoint requests/responses and media references with bounded pre/post-event windows. R2 replay needs filter/association/latch/clock/map state checkpoints; existing radar-only records do not magically include all R2 sensors. Original recording and recomputation are distinct. Corrupt/incompatible records fail visibly; no replay path reaches actuators.

**Detailed design:** [Replay](23_INCIDENT_RECORDING_AND_REPLAY.md).

## 31. Failure behavior

The 28-case campaign covers sensors, timing, transport/session integrity, map, compute, storage, brownout, peers and recovery. Each case defines lost and retained capabilities, state/message/evidence and common pass conditions. Deterministic software injections precede separately authorized hardware tests. No fault response or recovery is declared physically proven by this design review.

**Detailed design:** [Failure behavior](27_FAILURE_CAMPAIGN.md).

## 32. Security

Use TLS, provisioned device identity, authentication, RBAC, versioned/signed configuration and audit logs. CRC detects corruption but does not authenticate a sender. Separate monitoring/context from local authority, bound payloads/queues, and isolate replay/test modes. Credential lifecycle and adversarial tests are implementation tasks; no security certification is claimed.

**Detailed design:** [Security](35_SECURITY_ARCHITECTURE.md).

## 33. Novelty

The evidence-driven combination emphasizes source freshness/uncertainty, disagreement retention, route-aware constrained-road conflicts, capability degradation and incident explanation. Compare only with capabilities evidenced in Master‑1's competitor review. Standard algorithms are not claimed as inventions, and unknown competitor capabilities are not asserted absent.

**Detailed design:** [Novelty](30_NOVELTY_AND_DIFFERENTIATION.md).

## 34. Feasibility

Documented component interfaces and an existing software/robot base support staged implementation. Combined power, payload, thermal, USB, compute and network performance remain real integration risks, each with a release gate. The Pi is not a second AI engine. A measurement shortfall triggers scoped workload/operating-domain review before any formal hardware-change proposal.

**Detailed design:** [Feasibility](31_FEASIBILITY.md).

## 35. Viability

Plan modular replacement, calibration/maintenance records, staged software updates, network/storage sizing and fleet onboarding. Prototype component cost is not industrial installed cost. A later production carrier/rugged edge implementation, approved OEM interfaces and site support require a separate total-cost and approval assessment.

**Detailed design:** [Viability](32_VIABILITY_AND_SCALABILITY.md).

## 36. Impact

Expected mechanisms are improved warning/awareness, better contextual route decisions and replayable incidents supporting operational review. Measure false alerts, warning lead time, outages, availability and comparable cycle times before attributing benefit. No accident reduction, tonnage improvement or productivity percentage is invented.

**Detailed design:** [Impact](33_IMPACT_AND_BENEFITS.md).

## 37. Validation

Pin references, settings, calibration and environmental conditions per run; use independent reference uncertainty and run-level evaluation splits. Conduct clear-air, controlled artificial-aerosol and recovery tests, never call them Bailadila recreation. Numerical thresholds without authoritative requirement are proposed validation targets, not performance. Retain failed/partial runs and report coverage gaps.

**Detailed design:** [Validation](29_KPIS_AND_ACCEPTANCE.md).

## 38. Demo

The primary sequence lasts 180 seconds and shows the evidence story, degradation, reasoned constraints, a peer conflict and replay. It defaults to labelled simulation/replay and zero motion. Substitute physical evidence only after its commissioning gates; a separate extended technical demo covers details. No narrative deadline overrides a physical release hold.

**Detailed design:** [Demo](39_THREE_MINUTE_DEMO.md).

## 39. Industrial mapping

Map the prototype roles to rugged sensing/compute, an industrial local controller, approved OEM/CAN/J1939 information, existing dumper propulsion/braking and mine communications. Progress through shadow, advisory, supervised pilot and only then validated/approved intervention. Development boards, the consumer AP and acrylic chassis are not deployed mine hardware.

**Detailed design:** [Industrial mapping](34_INDUSTRIAL_DEPLOYMENT_MAPPING.md).

## 40. Limitations

R2 algorithms, services, physical bindings and comparative performance are design commitments, not completed software. Exact pins/mounts/power ratings remain withheld where evidence is missing. Real terrain/targets, environment, human response and mine reliability need testing. This package does not supersede R1 runtime with invented R2 functionality or certify safe operation.

**Detailed design:** [Limitations](36_CLAIM_MATRIX.md).

## 41. Implementation roadmap

Eighteen planning phases progress from baseline and power/interfaces through acquisition, contracts, perception, localization/navigation, fleet/conflicts, envelope/HMI/control room, endpoint, failures, aerosol evaluation and demonstration. Fixture development may proceed before hardware arrival; physical steps require named releases. Planning-phase numbers are distinct from current DISABLED_PHASE_1 and industrial rollout phases.

**Detailed design:** [Implementation roadmap](42_IMPLEMENTATION_ROADMAP.md).

## 42. Final budget reference

Master‑1 remains INR 192,150 electronics plus INR 55,000 integration/assembly allocations = INR 247,150 against INR 250,000, leaving INR 2,850 unallocated reserve. This is planning cost, not a new landed quote; owned parts are zero incremental acquisition, not zero economic value. Do not add premium sensors. Regional availability, actual delivery PIN, freight and arrival by 15 October 2026 require procurement verification.

**Detailed design:** [Final budget reference](../tark-r2-master/09_BUDGET_ALLOCATION.md).

## 43. Open issues

The 24-entry register assigns owner, evidence and exact blocked release. It preserves the three explicit handoff boundaries and also covers actual current/power/payload, camera/thermal/radar modes, datum/timing/workload/network, references/licenses, endpoint binding and feedback/age contract. None is silently resolved; no demonstrated primary-hardware incompatibility has justified a CR-M2.

**Detailed design:** [Open issues](45_OPEN_ISSUES_REGISTER.md).

## 44. Claim boundaries

MASTER ENGINEERING BLUEPRINT 2: PASSED means internally coherent engineering design ready for controlled implementation. It is not implementation completion, fabrication release, measured performance, physical verification or mine certification. The claim matrix, adversarial review and hardware gates govern all presentations. Existing production source, physical wiring and current zero-output authority remain unchanged.

**Detailed design:** [Claim boundaries](46_ADVERSARIAL_REVIEW.md).

### Supporting delivery index

The numbered files 01–47 in this directory form one package. In addition to the linked owners above: [GPIO reservations](03_ESP32_GPIO_RESERVATION.md), [software architecture](24_SOFTWARE_ARCHITECTURE.md), [algorithm catalog](25_ALGORITHM_CATALOG.md), [dataset strategy](26_DATASET_STRATEGY.md), [low-visibility experiment](28_LOW_VISIBILITY_VALIDATION.md), [22 flowcharts](37_FLOWCHARTS.md), [eight interconnect views](38_CIRCUIT_AND_INTERCONNECT_DIAGRAMS.md), [55 judge questions](40_JUDGE_QA.md), [12-slide engineering content](41_PPT_ENGINEERING_CONTENT.md), [software implementation order](43_SOFTWARE_IMPLEMENTATION_PLAN.md) and [hardware gates](44_HARDWARE_COMMISSIONING_GATES.md) provide the operational detail.

**Release disposition:** ready for controlled design-to-implementation work; not ready for unrestricted fabrication/energization or positive motor-output release. Resolve each applicable hold before its gate. No frozen primary hardware change is requested.

Master Engineering Blueprint 2 is complete and TARK R2 is ready to proceed into controlled hardware/software implementation without reopening the frozen primary hardware architecture.
