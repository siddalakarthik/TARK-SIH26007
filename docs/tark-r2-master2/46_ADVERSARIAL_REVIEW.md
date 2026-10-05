# 46 — Adversarial design review and completion audit

Revision M2-E1 • 2 October 2026. This is a document-level engineering review, not a software regression, external professional certification or physical test. Reviewer roles are analytical perspectives, not claims that those professionals independently signed the design.

## Review lenses

| Perspective | Attack | Design resolution | Owner document | Remaining evidence |
|---|---|---|---|---|
| NMDC mine engineer | A laboratory fog result is presented as haul-road protection. | Keep controlled artificial-aerosol scope, terrain/target coverage and site validation distinct. | [Detail](28_LOW_VISIBILITY_VALIDATION.md) | Mine-domain coverage and environmental qualification remain unmeasured. |
| Haulage operations manager | Frequent false warnings erase expected productivity gains. | Measure false-alert burden, downtime and cycle-time with comparable operating conditions; do not promise percentages. | [Detail](33_IMPACT_AND_BENEFITS.md) | Operator acceptance and matched site trials are required. |
| Automotive ADAS engineer | Correlated sources create artificially narrow uncertainty. | Retain source dependence, time/extrinsic uncertainty and unmatched evidence; do not multiply confidence scores. | [Detail](11_MULTISENSOR_FUSION.md) | Association/covariance calibration requires held-out reference runs. |
| Radar engineer | An empty target list becomes free-space evidence. | Separate valid-empty measurement from characterized contiguous coverage and enforce UNKNOWN outside evidence. | [Detail](08_RADAR_PERCEPTION.md) | Exact TI profile and target/environment coverage remain open. |
| Embedded systems engineer | Delayed frames or blocked TX outlive the claimed motor deadline. | Independent expiry scheduling, bounded queues and session retirement; document receipt-lifetime and missing wheel-schema limits. | [Detail](20_LOCAL_ENDPOINT_ARCHITECTURE.md) | Board binding, age argument and reviewed feedback revision required before positive authority. |
| Power engineer | Shared returns, USB backfeed or ENA jumpers defeat fail-disabled behavior. | Separate power roles, map intentional references, protect branches and independently interrupt traction; no false reset-safety claim. | [Detail](04_POWER_ARCHITECTURE.md) | Exact ratings, inrush, thermal and boot behavior need qualification. |
| Functional-safety engineer | A five-state display is mistaken for certified control. | Define capability intersection, immediate escalation, controlled recovery and independent cutoff; exclude certification claims. | [Detail](19_OPERATING_AUTHORITY_STATE_MACHINE.md) | Hazard analysis and industrial approval remain outside prototype proof. |
| Localization engineer | Map snapping hides RTK/multipath or a common bad base. | Maintain datum, quality, covariance and plausible edge candidates; no independent-truth claim from FIXED. | [Detail](13_LOCALIZATION_ENGINE.md) | Independent reference and common-error tests remain required. |
| AI engineer | Adjacent-frame test leakage yields impressive but invalid accuracy. | Split by run, retain failures, pin models/modes and distinguish public benchmarks from mine validation. | [Detail](26_DATASET_STRATEGY.md) | Dataset licensing and held-out domain performance remain open. |
| Cybersecurity engineer | CRC or a trusted-looking browser becomes authorization. | Use authenticated device identity, TLS, role control and signed/versioned configuration; replay cannot enter live authority. | [Detail](35_SECURITY_ARCHITECTURE.md) | Provisioning, threat tests and operational key handling are later implementation work. |
| SIH judge | A polished diagram is claimed as functioning hardware. | Use maturity labels, evidence-linked demonstration and separate design/fixture/physical claims. | [Detail](36_CLAIM_MATRIX.md) | No new test result or implementation is produced by this document. |

## Required attack cases

| Attack | Required behavior / acceptance boundary | Reference |
|---|---|---|
| Fog defeats RGB | Remove unsupported semantic capability; keep independently qualified radar/thermal, not inferred class. | [Detail](09_RGB_PERCEPTION.md) |
| Thermal becomes ambiguous/isothermal or enters FFC | Invalidate affected frame/region; do not fabricate temperatures, range or object class. | [Detail](10_THERMAL_PERCEPTION.md) |
| Radar returns no target | Valid-empty does not establish clear space; no positive envelope from silence. | [Detail](18_STOPPING_AND_SAFE_OPERATING_ENVELOPE.md) |
| RTK becomes FLOAT | Show exact quality; enlarge uncertainty and withhold unsupported maneuver/conflict precision. | [Detail](13_LOCALIZATION_ENGINE.md) |
| Both rovers lose corrections | Treat common error; independent local observations remain, cooperative assurance may become UNKNOWN. | [Detail](17_BLIND_CURVE_AND_JUNCTION_CONFLICT.md) |
| Wi-Fi dies | No loss of local sensing/expiry; corrections and remote context age out explicitly. | [Detail](16_FLEET_TELEMETRY_AND_V2X.md) |
| Second-node telemetry freezes | Retain stale marker and uncertain occupancy; never convert absence to clearance. | [Detail](17_BLIND_CURVE_AND_JUNCTION_CONFLICT.md) |
| Browser attempts direct drive | No direct-drive API/role in the design; context writes cannot raise local authority. | [Detail](22_TARK_COMMAND_PLATFORM.md) |
| Jetson crashes | Future endpoint must expire independently; current outputs stay zero and cutoff is separate. | [Detail](20_LOCAL_ENDPOINT_ARCHITECTURE.md) |
| Sensors disagree | Keep matched, unmatched and disagreement evidence; no forced confidence upgrade. | [Detail](11_MULTISENSOR_FUSION.md) |
| Sensor reconnects | New identity/epoch and calibration/freshness/recovery gates before usable status. | [Detail](19_OPERATING_AUTHORITY_STATE_MACHINE.md) |
| Wheels slip or unwrap is ambiguous | Invalidate/downgrade wheel aiding, retain wheel-response terminology and motion uncertainty. | [Detail](12_VEHICLE_MOTION_MODEL.md) |
| IMU drifts | No long-term inertial navigation claim; covariance grows and aiding is bounded. | [Detail](13_LOCALIZATION_ENGINE.md) |
| Mine map is stale | Version/validity gate; do not display confident guidance from an unapproved map. | [Detail](14_MINE_NAVIGATION_GRAPH.md) |
| Road closes | Invalidate affected route and replan only on authorized open edges; closure cannot be overridden by desired arrival time. | [Detail](15_DRIVER_NAVIGATION.md) |
| Storage fills | Bound queues, record loss status/counters, preserve local loop; evidence completeness claim removed. | [Detail](23_INCIDENT_RECORDING_AND_REPLAY.md) |
| Network latency increases | Use age and clock uncertainty, drop queued stale observations and never renew old authority. | [Detail](07_EVIDENCE_AND_DATA_CONTRACT.md) |
| Vehicle enters unmapped road | Position can remain observable but route instructions/conflict geometry become unavailable. | [Detail](15_DRIVER_NAVIGATION.md) |
| Hardware overheats | Health/deadline degradation removes affected capability; do not assume rated compute remains available. | [Detail](24_SOFTWARE_ARCHITECTURE.md) |
| Future timestamp appears | Reject outside clock bounds; future age must not become negative/fresh. | [Detail](07_EVIDENCE_AND_DATA_CONTRACT.md) |
| Old valid command is delayed in transport | V2 receipt TTL does not prove original age; positive-output release requires reviewed age/latency constraint. | [Detail](20_LOCAL_ENDPOINT_ARCHITECTURE.md) |
| Physical cutoff state is inferred from communication silence | Without actual feedback, report UNKNOWN; no auxiliary contact is invented. | [Detail](04_POWER_ARCHITECTURE.md) |
| Motor enable jumpers are mistaken for reset inhibition | Jumpers do not establish fail-disabled design; separate enable/reset release is mandatory. | [Detail](03_ESP32_GPIO_RESERVATION.md) |
| Receiver STATUS is assumed to carry wheel samples | Current schema has no such payload; version host/firmware/vectors together before use. | [Detail](20_LOCAL_ENDPOINT_ARCHITECTURE.md) |

## Documentation defects corrected during final review

The new ICD originally reused generic direction/return descriptions too broadly. These were corrected per interface: Lepton data flows toward PT3; active-antenna RF flows toward the receiver while bias flows toward the antenna; motor requests, switched motor power, display data, Ethernet and Wi-Fi now have specific semantics. Wireless paths have no invented cable voltage/return. The protected traction node starts after F-T; reset inhibition and cutoff feedback are not assumed. These are corrections within this new design package, not changes to physical wiring or frozen components.

The design also explicitly separates current V2 software capabilities from future wheel-response schema, physical scheduler/USB/watchdog and positive-command age requirements. These remain implementation gates, not assertions that firmware was modified here.

## Master‑2 consistency checklist

All findings below are DESIGN CONSISTENCY PASS, subject to their explicit measurement and release holds.

| Check | Finding | Evidence |
|---|---|---|
| HARDWARE | Master‑1 selections retained; three explicit handoff boundaries remain. | [Detail](01_COMPLETE_SYSTEM_ARCHITECTURE.md) |
| INTERFACES | Each selected device has a host/interface owner; logical pins remain gated. | [Detail](02_HARDWARE_ICD.md) |
| POWER | Each load has a rail/category; unknown ratings are holds, not guessed numbers. | [Detail](04_POWER_ARCHITECTURE.md) |
| TIME | Observation/reception/processing/clock-domain metadata is explicit. | [Detail](07_EVIDENCE_AND_DATA_CONTRACT.md) |
| HEALTH | Connected, fresh, valid, usable and characterized coverage are distinct. | [Detail](07_EVIDENCE_AND_DATA_CONTRACT.md) |
| LOCALIZATION | FIXED/FLOAT/degraded quality and uncertainty are visible. | [Detail](13_LOCALIZATION_ENGINE.md) |
| NAVIGATION | Ambiguous localization suppresses confident maneuver instructions. | [Detail](15_DRIVER_NAVIGATION.md) |
| FLEET | Missing peer evidence cannot mean empty road. | [Detail](16_FLEET_TELEMETRY_AND_V2X.md) |
| RADAR | No-target is not proven free space. | [Detail](08_RADAR_PERCEPTION.md) |
| THERMAL | No fabricated range or unsupported radiometry. | [Detail](10_THERMAL_PERCEPTION.md) |
| RGB | No image-quality-to-fog-metres conversion without calibration. | [Detail](09_RGB_PERCEPTION.md) |
| MOTION | Wheel response is not guaranteed ground speed. | [Detail](12_VEHICLE_MOTION_MODEL.md) |
| TTC | Only valid qualified closing geometry gives numeric TTC. | [Detail](08_RADAR_PERCEPTION.md) |
| STOPPING | No invented industrial braking parameters. | [Detail](18_STOPPING_AND_SAFE_OPERATING_ENVELOPE.md) |
| AUTHORITY | Faults intersect/reduce capabilities; recovery is gated. | [Detail](19_OPERATING_AUTHORITY_STATE_MACHINE.md) |
| NETWORK | Browser/network loss cannot disable independent local supervision. | [Detail](24_SOFTWARE_ARCHITECTURE.md) |
| CONTROL ROOM | Monitoring and bounded operational context, not arbitrary drive. | [Detail](22_TARK_COMMAND_PLATFORM.md) |
| ENDPOINT | Receiver expiry distinct from end-to-end age and hardware proof. | [Detail](20_LOCAL_ENDPOINT_ARCHITECTURE.md) |
| REPLAY | Original provenance retained; REAL/SIMULATION/REPLAY separate. | [Detail](23_INCIDENT_RECORDING_AND_REPLAY.md) |
| CLAIMS | No certification, guaranteed collision prevention or guaranteed production gain. | [Detail](36_CLAIM_MATRIX.md) |

## Change control and disposition

No demonstrated incompatibility requiring a frozen primary component substitution was established. **CR-M2: none issued.** Unknown geometry, exact board pins, regional SKU purchasing and unmeasured performance are not speculative incompatibility requests. [45](45_OPEN_ISSUES_REGISTER.md) identifies the owner, needed evidence and exact release each item blocks.

The PASS criterion is coherent design ready for controlled implementation—not fabrication readiness, completed R2 software, physical verification or mine approval. Current R1 production code and traction authority are unchanged. No purchases, hardware access, energization, flashing, commits or pushes are part of this task.

## Artifact verification

Algorithm arithmetic checks validate equations only; they do not test the application or measure hardware.

## Final verification results — 2 October 2026

| Check actually performed | Result |
|---|---|
| Exact document names against Master‑2 request | 47/47 present; no missing or extra numbered deliverable |
| Local Markdown reference targets | 55 distinct local targets checked; 0 missing |
| ICD structure | 39 connection records, each with all 21 requested field rows |
| Presentation/review coverage | 22 required flowcharts; 55 judge questions; 12 slide-content sections |
| Roadmap/consolidation | 18 planning phases (0–17); 44 consolidated blueprint sections |
| Failure/open-item coverage | 28 fault rows; 24 open issues with owner/evidence/release boundary |
| Markdown structure | No unbalanced code fences or inconsistent table column counts found |
| Equations, independent inline arithmetic | 80 stopping-inversion cases; maximum absolute distance residual 2.842e-14 in the synthetic test units; 160 delay/distance monotonic comparisons; 4 analytic CPA cases passed |
| Wheel resolution and timing arithmetic | 360/16384 = 0.02197265625 degrees/code (resolution, not accuracy); primary demo intervals total 180 seconds |
| Read-only BOM reconciliation | 38 rows; all quantity × unit extensions agree; INR 1,92,150 + INR 55,000 = INR 2,47,150; INR 2,850 headroom |
| Master‑1/historical handoff preservation | SHA‑256 compared at start/end of final continuation: all 24 source/historical files unchanged |
| Tracked repository source scope | Git working/staged diffs empty and diff whitespace check clean; pre-existing unrelated untracked files left alone |
| Production/hardware tests | Not run: design-only task; no COM/USB/I2C access, flashing or motor operation |

Mermaid source received structural and semantic review; the 26 Mermaid blocks across the package were **not rendered or checked with a Mermaid parser** in this pass. The requested editable diagram sources are supplied; no screenshot/PDF layout verification is claimed. The arithmetic checks evaluate documented equations using synthetic numbers, not production software or physical safety performance.

Further final-review clarifications: explicit zero-speed interval guards avoid division by zero in blind-curve prediction; named task dependency profiles make fault-matrix conditional states reproducible and prevent automatic degradation to a weaker profile.

Completion scope: the final continuation added documents 40, 41, 42, 45, 46 and 47 and corrected interface descriptions, interval guards and task-profile clarity in 02, 17 and 19. Earlier completed documents were retained. This package contains no production implementation changes.

**MASTER ENGINEERING BLUEPRINT 2: PASSED.** Proceed only through the controlled implementation roadmap and applicable hardware gates. R2 software implementation, physical binding and measurements remain future work, explicitly scoped—not claimed completed by this design verdict.
