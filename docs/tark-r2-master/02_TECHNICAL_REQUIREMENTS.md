# TARK R2 — technical requirements

Revision M1 • 1 October 2026 • SIH26007 research demonstrator.

## Authority and scope

The user's Master Hardware Prompt 1 is authoritative for this package: INR 250,000 maximum **additional planning spend**, owned assets at zero additional acquisition cost, no procurement or delivery gate, no application/firmware/PPT changes. Earlier Batch-A files remain historical and unchanged. This is not permission to energize hardware or release an industrial safety product.

Evidence vocabulary: **PUBLISHED** = attributable manufacturer capability; **TARGET** = proposed test objective; **MEASURED** = result with retained test evidence. This package contains no new measured hardware performance. User-reported robot movement/timeout behavior is retained as a report, not transferred to the frozen software release or HEMM braking.

## Requirement-to-hardware map

| ID | SIH need / requirement | Selected evidence or implementation resource | Completion evidence required later |
|---|---|---|---|
| R01 | Obstacles and relative motion despite poor visible contrast | One IWR1843BOOST front radar | Target-dependent range/velocity/angle errors, missed detections and false alarms |
| R02 | Understand obstacle class, road context and signs | B0200 RGB camera | Calibrated lens/exposure, task-specific classification precision/recall by condition |
| R03 | Complement RGB for thermal contrast | Lepton 3.5 plus PureThermal 3 | Thermal contrast/association versus range, FFC interruptions and aerosol condition |
| R04 | Vehicle position, road assignment, route guidance | Three LG290P kits: A rover, B rover, fixed base | Surveyed reference frame, fix-state/correction-age behavior and lateral error |
| R05 | Blind-curve/junction cooperative warning | Two physical rover nodes, local AP and route graph | Time-to-conflict intervals with position, clock, motion and map uncertainty |
| R06 | Short-term motion/heading continuity | BNO085 SPI IMU | Axis alignment, bias/drift, vibration and magnetic-disturbance characterization |
| R07 | Verify left/right wheel response | Two magnetic absolute-angle sensing paths | Measured wheel geometry, angle validity, direction and sample-gap checks |
| R08 | Execute local processing without internet/cloud | One Orin Nano Super 8 GB | End-to-end latency, memory/storage/thermal and failure-load profiles |
| R09 | Maintain bounded prototype endpoint behavior | Owned ESP32-S3 | Exact PCB/pin identity plus reviewed command/session/expiry implementation on actual board |
| R10 | Driver sees state, reason, next maneuver and uncertainty | 7-inch HMI plus buzzer | Readability and comprehension; stale/unknown indication; audible warning recognition |
| R11 | Evidence capture and incident replay | 500 GB NVMe | Bounded retention, timestamp integrity, loss counters and replay provenance |
| R12 | Local fleet monitoring and corrections | Wi-Fi AP, Ethernet main node, Pi second node, laptop base/control room | Measured traffic/latency/loss; offline and stale-peer behavior |
| R13 | Preserve operation through nonlocal failures | Local sensors/compute/endpoint independent of control-room availability | Network/browser removal does not grant additional motion authority |
| R14 | Separate electrical noise/energy and protect circuits | Dedicated electronics power; separate traction; protected conversion/fusing | Prompt-2 power, grounding, inrush, reverse polarity and thermal review |
| R15 | Independent manual removal of traction energy | Rated latching DC disconnect category | Verified load/rating, accessible actuation, no automatic restart after reset |
| R16 | Stable geometry and experimental references | Mast/brackets, calibration/reference/test allocations | Mount deflection, extrinsics, reference uncertainty and repeatability |
| R17 | Quantify low-visibility performance honestly | Controlled artificial-aerosol low-visibility experiment | Condition record, optical contrast method, repeated matched clear/aerosol runs |
| R18 | Feasible complete integration budget | All electronics, power, mounts, test and reserves in BOM | Formula reconciliation <= INR 250,000; estimates are not quotes |

## Architecture boundaries to preserve in Prompt 2

Sensors → observations with origin/time/quality → localization/perception → evidence envelope and risk → bounded supervisory request → local controller → permitted prototype endpoint. A parallel observation path feeds driver/control-room HMI and recording. A physical traction disconnect is independent of the application. No browser or peer packet is direct motor authority.

The hardware supports future R2 implementation; this document does not claim those new drivers, fusion, route guidance or two-rover services already operate together. It does not alter the current software's `DISABLED_PHASE_1` authority.

Unknown or stale evidence never proves a clear road. Radar radial velocity is not automatically longitudinal closing speed; wheel response is not ground truth; a receiver's RTK FIX flag is not an integrity guarantee. Heading at rest is not supplied by a single-antenna receiver. Map routes are not surveyed haul-road geometry merely because they are displayed.

## Frozen owned-hardware boundary

- Reuse Pi 3B+, SD card, ESP32-S3, robot drivetrain/chassis, webcam and laptop in the roles listed in the BOM.
- GPIO4 → IN1 and GPIO5 → IN2 are retained user-reported mappings. **GPIO16/17 are under investigation**, superseding the earlier preliminary inventory reply. No final right-channel pins or encoder pins are assigned here.
- Exact PCB, motor ratio/stall current, battery chemistry/protection, charger, wheel/mount geometry and switch/relay ratings remain unknown. No values are inferred from appearance or a 7.78 V reading.
- L298N onboard 5 V must not supply Pi, Jetson or ESP32. ENA/ENB jumpers do not establish variable-speed control. The bare relay and unrated red switch are not selected safety interruption devices.
- The damaged LM2596 is permanently excluded. No HEMM propulsion/braking equivalence follows from a TT-motor model.

## Non-goals

No autonomous mine-driving release, certified collision-avoidance guarantee, production-gain percentage, blanket all-weather claim, physical wiring master, hardware test, purchase or code modification. Side/rear premium sensing is outside this first front-facing demonstrator's coverage.
