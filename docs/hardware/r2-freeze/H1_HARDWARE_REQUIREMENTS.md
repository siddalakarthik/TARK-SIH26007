# TARK R2 — H1 hardware requirements

Revision A0, 1 October 2026. **BATCH A FAILED / NOT RELEASED FOR PROCUREMENT OR ENERGIZATION.**

This is the requirements baseline for the proposed R2 moving research demonstrator, not a claim that its hardware is built or verified. H1, H2 and H3 cannot become a released freeze until the checkpoint passes. The additional-expenditure ceiling is INR 205,000. Delivery target: Hyderabad, 15 October 2026; actual six-digit PIN remains missing.

## Evidence boundary

The latest user inventory is the authority for what the team reports owning and operating. It does not establish unidentified ratings. The frozen R1 software remains a separate zero-output evidence release (`DISABLED_PHASE_1`). The reported ASCII-controlled robot and approximately 500 ms receive timeout are not Protocol V2 physical verification, measured stopping time, or a certified safety function. No software, wiring, firmware or hardware was changed in this batch.

## Requirements and traceability

All IDs below use the prefix `TARK-HW-REQ-`. References A01–A26 are BOM IDs; R01–R08 are explicitly costed integration reserves. GAP references identify requirements not satisfied by an exact selected item, rather than hiding omissions.

| ID | Hardware SHALL requirement | Rationale | Later verification | Subsystem / H2 allocation |
|---|---|---|---|---|
| 001 | The demonstrator SHALL support controlled forward, reverse, left, right and stop trials on the existing small robot, only after electrical and mechanical release. | Demonstrate physical integration without claiming HEMM dynamics. | Contained low-energy commissioning and recorded direction tests. | A16, A18–A21; GAP-MOTION |
| 002 | Local perception SHALL have one primary mmWave radar, one RGB channel and one complementary thermal channel. | Different physical evidence, not redundant brand names. | Separate acquisition and channel-removal tests. | A02–A05 |
| 003 | Radar SHALL provide documented processed target measurements sufficient to derive supported range, angle and radial-relative-motion evidence in a characterized test domain. | Avoid unsupported long-range claims and undocumented decoding. | Pin radar application/SDK version; reference targets and decoded packet checks. | A02 |
| 004 | RGB SHALL provide color images through a documented Linux-compatible interface with a fixed recorded lens configuration. | Semantic evidence and repeatable calibration. | Enumerate formats and controls; record calibration and exposure behavior. | A03 |
| 005 | Thermal SHALL have a complete host acquisition chain, not an unconnected sensor core. | Core cost alone is not system cost. | Core/interface/cable identification, frame and shutter-event checks. | A04, A05, A14 |
| 006 | Acquisition SHALL permit host timestamp alignment with documented buffering and age; USB arrival time SHALL NOT be represented as simultaneous exposure time. | Asynchronous channels require measured temporal uncertainty. | Later timing experiment and dropped-frame logs. | A01–A08, A11 |
| 007 | The mounts SHALL permit rigid and repeatable radar/RGB/thermal geometric calibration with unobstructed sensor apertures. | Association needs known frames. | Dimension review, extrinsic calibration and remount-repeatability tests. | A20, R02, R04; GAP-MECHANICAL |
| 008 | One main edge computer SHALL own local perception, association, tracking, decision-support computation, recording and local services. | Avoid competing command/computation owners. | Later workload profiling and authority review. | A01, A10 |
| 009 | The compute configuration SHALL accommodate concurrent radar, RGB, thermal, rover GNSS, supervisor and HMI interfaces with a verified USB power/bandwidth allocation. | Port count alone does not establish operability. | Concurrent-load, reconnect, bandwidth and power tests. | A01–A06, A09, A11, A14, A16 |
| 010 | Compute SHALL retain an appropriate cooling assembly and service clearance. | Sustained load and enclosure heat matter. | Temperature/throttling measurements at selected load and ambient conditions. | A01, R02 |
| 011 | Main recording SHALL use dedicated nonvolatile storage; the second-node boot card SHALL NOT be double-counted as main recording storage. | Isolate capacities and devices. | Capacity, sustained-write and power-loss recovery tests. | A10, A23 |
| 012 | Local supervision SHALL be assigned to the existing ESP32-S3 endpoint after exact board verification. | Keep low-level supervision separate from high-level compute. | Board identity, boot/output state and later timeout integration tests. | A16; GAP-IDENTITY |
| 013 | The endpoint hardware SHALL support bounded outputs and a later no-automatic-restart policy after reconnect or power restoration. | A restart must not retain a motion request. | Later firmware/board integration; not implemented by purchasing parts. | A16, A18, R01 |
| 014 | Independent physical traction-power interruption SHALL not depend on the browser, network, Jetson or a firmware command. | Software stop and power interruption are different functions. | Rated-device review and authorized interruption tests. | GAP-CUTOFF, R01 |
| 015 | Wheel sensing SHALL measure rotational response and direction on both sides with a known resolution and documented endpoint interface. | Command is not feedback. | Unpowered fit check followed by later count/direction/reference tests. | GAP-ENCODER, A16, R02, R04 |
| 016 | Wheel-response evidence SHALL remain distinct from true ground speed and slip-free odometry. | TT wheels can slip. | Independent position reference during later trials. | GAP-ENCODER, A06, R04 |
| 017 | The L298N/TT combination SHALL only be retained for energized R2 operation after voltage, paired-motor startup/stall and thermal compatibility are established. | Working once does not establish ratings or continuous capacity. | Manufacturer identity and later current-limited measurements under an approved plan. | A18–A21; GAP-MOTION |
| 018 | Battery chemistry, protection and charging identity SHALL be established before reuse or charger selection. | A 7.78 V reading does not identify chemistry. | Label, supplier record and protection inspection. | A21, A22, R01; GAP-POWER |
| 019 | Compute and sensors SHALL receive suitable protected regulated supplies; the L298N onboard 5 V rail SHALL NOT power Pi or ESP32. | Motor transients and unknown regulator capability. | H5 power budget, rail-ripple/sequence and protection review. | R01, A01, A02, A05–A09, A11, A15, A16 |
| 020 | The main vehicle and second physical node SHALL each have an actual GNSS receiver and report position-quality state. | A duplicated map marker is not a second node. | Two separately identified outdoor tracks. | A06, A07, A15 |
| 021 | RTK experiments SHALL use two rovers and one shared local base with compatible antennas and documented correction support. | Self-contained correction provision without assuming NTRIP access. | Base configuration/reference-position record, RTCM delivery and fixed/float/no-fix tests. | A06–A08, A12, A14, A25, A26 |
| 022 | GNSS quality/freshness loss SHALL remove claims of precise positioning without being treated as loss of local radar sensing. | Independent evidence domains. | Later correction-loss, blockage and stale-message experiments. | A06–A08, A01 |
| 023 | Second-node computation SHALL only relay positioning/health and receive corrections, not duplicate main perception or motion authority. | Reuse the Pi 3B+ for a distinct workload. | Process/port/authority review and telemetry test. | A15, A23 |
| 024 | A local Wi-Fi network SHALL support node telemetry, correction transport and monitoring without a public-internet dependency. | Demonstration continuity. | WAN-disconnected network test and measured load/latency. | A12, A15, A25 |
| 025 | The local driver display SHALL show state, reason and evidence quality while remaining monitoring-only. | Clear assistance rather than browser motion control. | Later HMI readability/authority review. | A09, A13, A01 |
| 026 | Control-room monitoring SHALL use a separately identified existing host on the local network. | Remote observation without a second Jetson. | Host inventory, local dashboard and base-relay checks. | A25, A12 |
| 027 | Device connectors, cable power capacity and attachment shall be documented before integration; charge-only USB cables SHALL NOT be used for data paths. | Avoid missing acquisition links. | Inventory/continuity and device enumeration later. | A14, A26, R03 |
| 028 | Serviceable mounts SHALL protect boards from shorts and strain while permitting replacement and identification. | Exposed development boards are not mine enclosures. | Mechanical and access review. | A20, R02, R03 |
| 029 | Calibration/test hardware SHALL be separately budgeted. | Accuracy and repeatability require references. | Test-plan and fixture inspection. | R04 |
| 030 | Low-visibility trials SHALL have approved aerosol/fog, references, ventilation and containment rather than uncontrolled exposure of people or electronics. | Safe, interpretable experiments. | H10 risk assessment and controlled protocol. | R05, R04, R02 |
| 031 | Cost SHALL include complete acquisition assemblies, taxes/freight uncertainty and protected later-integration reserves within INR 205,000 additional expenditure. | Prevent a sensor-only budget. | Quote reconciliation and H2 budget audit. | All BUY rows; R01–R08 |
| 032 | Every delivery-critical part SHALL have a supplier-confirmed path to Hyderabad by 15 October, or an explicitly documented procurement risk. | Stock count is not arrival evidence. | Dated quote against actual PIN and shipment terms. | All BUY rows |
| 033 | No student part SHALL be claimed as a mine-qualified substitute for the corresponding industrial subsystem. | Honest scalability argument. | Claim review against manufacturer scope and measured evidence. | All rows; claim matrix |
| 034 | R1 evidence and software SHALL remain unchanged; current team-reported robot motion SHALL remain a separate evidence category. | Prevent false convergence claims. | Git scope check and documentation review. | All documents; no hardware allocation needed |
| 035 | Owned hardware SHALL have a recorded verification requirement; the burnt LM2596 SHALL remain permanently excluded. | Ownership does not establish suitability. | Photo/measurement register and receipt inspection. | A15–A25; exclusions |

## Industrial function represented—not qualified hardware

| Student hardware/function | Industrial function represented | Boundary |
|---|---|---|
| TT drivetrain and L298N | Vehicle motion-output interface | No HEMM braking, inertia, traction or stopping equivalence |
| Wheel pickups, not yet selected | Approved vehicle-motion source, potentially an approved CAN/J1939 interface | No vehicle-bus access selected or implemented here |
| ESP32-S3 | Local supervisory endpoint concept | Not a safety ECU or certified watchdog chain |
| IWR1843BOOST | Radar-perception development | EVM, not a mine-ready radar installation |
| RGB and Lepton assembly | Complementary visible/LWIR observation | No all-weather detection guarantee |
| Jetson dev kit | Edge processing | Production carrier, environmental qualification and workload validation remain separate |
| GNSS rovers/local base | Positioning and cooperative context | Outdoor correction-dependent research, not always-centimetre navigation |
| Local AP/HMI | Fleet/control-room communications and driver assistance | No mine-wide coverage, C-V2X certification or remote motion authority |

No numeric detection range, inference FPS, stopping distance, battery runtime or positioning accuracy is frozen by this requirements file.
