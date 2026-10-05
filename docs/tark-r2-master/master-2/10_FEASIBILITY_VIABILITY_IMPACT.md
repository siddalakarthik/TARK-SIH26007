# Master-2 — feasibility, viability, impact and industrial mapping

## 1. Feasibility conclusion

The frozen stack is a technically coherent **research-demonstrator platform**, not a validated mine retrofit. Its feasibility depends on measured integration: simultaneous Jetson load, powered USB topology, real camera/thermal formats, RTK reference/antenna conditions, timing, electrical protection and the acrylic platform's payload. This package supplies a testable design without claiming those gates have passed.

| Dimension | Why the selected platform is plausible | Principal risk / evidence required |
|---|---|---|
| Sensing | Radar geometry, visible semantics and LWIR contrast provide complementary observations | Coverage, common failures and association must be characterized; sensor count is not evidence of safety |
| Compute | One GPU-capable edge platform avoids relying on Pi 3B+ for flagship inference | Model/format selection and concurrent timing/RAM/thermal tests; TOPS is not application FPS |
| Localization | Two physical RTK-capable rovers and local base support a cooperative course experiment | Corrections, datum, multipath, heading and map uncertainty; no automatic lane integrity |
| Control | Existing portable V2 supervision provides a tested software basis | Physical USB/boot identity/scheduler/watchdog binding and future wheel telemetry still need implementation/review |
| Mechanics | Reusing the drivetrain keeps the experiment focused on assistance | Actual total mass/CG/mount stiffness may prevent a fully mobile payload without detail revision |
| Energy | Separate electronics/traction categories avoid relying on the L298N rail | Actual peak current, converters, returns, pack/charger and disconnect qualification |
| Offline operation | Local compute/storage/AP and graph-based guidance do not require cloud decisions | Preloaded lawful map/course data, bounded networking and failure-visible HMI |
| Demonstration | Separate sensing, software fault and restrained model-response evidence can be clearly shown | Never present separate videos/simulations as one physically integrated run |

## 2. Budget lock and reserve policy

M1 is unchanged: exact/bundled electronics allocation INR 192,150; wheel/power/mechanics/harness/calibration/experiment/spares/reserves INR 55,000; owned acquisition INR 0. **Total INR 247,150. Remaining INR 2,850 remains reserve.** No new premium sensor, display, computer or radio is authorized.

M1 already contains INR 5,000 price uncertainty, INR 5,000 contingency and INR 4,000 ordinary spares; these are not extra headroom to count twice. The INR 18,000 power and INR 6,500 mount allocations must fund the qualified assemblies specified by their categories. If actual detailed parts exceed an allocation, record the variance and obtain a controlled budget decision. Never silently remove protection or use damaged parts to make the total appear compliant.

Jetson 0000/0007 is only the later regional-purchase check. Preserve the Orin Nano Super 8 GB platform. Do not apply an observed 0000 price to 0007 as a fact; a different invoice is a budget update, not automatic architecture redesign.

This is **additional student research spending**, not total historical project cost or a commercial per-dumper price. It excludes student labor, owned laptop/hardware value, certified industrial components, mine survey and validation/approval costs. No commercial bill-of-materials saving or ROI is claimed.

## 3. Implementation viability and work packages

| Package | Deliverable | Dependency / exit |
|---|---|---|
| W1 As-built/detail closure | Photos/labels, wheel/chassis dimensions, reviewed electrical/mount drawings | Resolve actual ratings and pin reservations before powered work |
| W2 Acquisition integration | Single-owner TI/B0200/PT3/LG290P/BNO085 adapters and diagnostics | Documented delivered firmware/formats; software tests then bench evidence |
| W3 Endpoint/wheels | Reviewed board binding and versioned wheel-response extension through existing service | No guessed GPIO/USB/watchdog; no motion enable hidden in telemetry work |
| W4 Calibration/time | Transforms, biases/reference frames and timing bounds | Independent reference data and repeatable fixtures |
| W5 Perception/envelope | Qualified tracking/association/uncertainty and shadow R2 envelope | Recorded data, controlled parameters and adversarial regression |
| W6 Navigation/fleet | Local graph, localization quality, guidance and conflict intervals | Reference course/map, two physical nodes and bounded authenticated peer data |
| W7 HMI/replay | Versioned projections, evidence explanations and extended replay | Single runtime, complete new input/checkpoint coverage, no browser authority |
| W8 Validation | Gate-linked evidence package, measured limitations and SIH demonstration | No physical/industrial claims beyond test scope |

These are ordered engineering dependencies, not guaranteed calendar estimates. Hardware delivery, staffing and data availability are not known sufficiently to promise completion dates. The present request completes design documents, not these future implementation packages.

## 4. Operational viability

At startup, an operator needs identity/configuration/calibration status, source availability, map/reference version, communication age and explicit traction phase. At shutdown, recordings close with a truthful complete/interrupted state. Field maintenance needs cleaning/inspection, battery/charger care per manufacturer, connector strain checks, calibration validity and bounded storage management.

Ownership must be assigned for map/restriction approval, vehicle identity, base setup, parameter release, software/model versions and incident review. Without that workflow, more accurate hardware can still publish the wrong road, stale restriction or wrong base reference.

Driver acceptance depends on timely, understandable warnings and controlled nuisance rate. The system should explain the binding limitation and preserve operator trust by saying UNKNOWN rather than inventing certainty. Control-room observation loss must not become a local motion dependency.

## 5. Impact measurement — not invented improvements

| SIH outcome | Demonstrator-level measurable evidence | Industrial outcome requiring later study |
|---|---|---|
| Improved situational awareness | Hazard recognition/action selection time, correct interpretation of stale/unknown data | Cab/operator performance in representative weather and workload |
| Reduced collision risk | Missed/false warnings and earliest useful warning under controlled trajectories | Exposure-adjusted incidents/conflicts with independent safety review; no prevented-accident count from simulation |
| Guidance/continuity | Successful course navigation, valid-position/route availability and graceful-degradation time | Availability over actual pit roads, monsoon conditions and traffic |
| Haulage efficiency | Controlled-route task duration with equal safety constraints | Matched loaded/empty haul-cycle times, queues, slope/load/weather and operator effects |
| Fleet utilization | Logged available/restricted/unavailable intervals with causes | Shift-level productive time with vehicle/job assignment controls |
| Production-loss reduction | No direct prototype production measurement | Tonnes/shift, ore evacuation and downtime with suitable baseline and confounder control |
| Monitoring/decision support | Event reconstruction completeness, latency and operator comprehension | Multi-shift command-room workload and operational decision quality |
| Scalability | Bounded simulated peer/client load and one real peer | Site coverage, infrastructure capacity, maintenance and integration cost |

Useful definitions: `cycle_time = loading + loaded_travel + dump_queue + dumping + empty_travel + load_queue`; `availability = eligible_operating_time / planned_time`, with downtime definitions fixed in advance. `relative_cycle_change = (baseline - assisted) / baseline` is meaningful only for comparable operations and uncertainty reporting. Higher speed, lower simulated TTC or fewer alerts alone is not evidence of safer productivity.

A field evaluation needs matched conditions or an approved controlled design, adequate exposure/sample size, independent incident definitions and no intentional hazardous encounter. No numerical safety/production percentage or commercial payback is asserted here.

## 6. Industrial mapping without hardware substitution now

| Research function | Industrial direction | Additional evidence/engineering |
|---|---|---|
| Front sensing stack | Qualified installed radar/cameras and coverage architecture | Environment, EMC, mounting, cleaning, diagnostics and relevant-target validation |
| RTK/IMU/navigation | Surveyed mine datum, managed corrections, map integrity and qualified localization | Pit-wall multipath/outage, wrong-road prevention, reference maintenance |
| Wheel response | OEM-approved CAN/J1939 or qualified motion source, read-only initially | Signal semantics, units, freshness, slip and OEM approval; no arbitrary CAN writes |
| ESP32 model supervision | Appropriate approved vehicle/safety-controller integration after hazard analysis | Independent diagnostics, safety lifecycle and verified failure response |
| TT/L298N motion | Assistance-chain concept only | No scaling of torque, brake force, stopping distance or downhill stability to HEMM |
| Driver display/buzzer | Cab-suitable HMI and alarm design | Human factors, noise/glare, acknowledgement and nuisance-warning qualification |
| Consumer edge/storage/network | Industrial compute/power/recording and site-selected communication | Vehicle transients, ruggedness, cybersecurity, retention and lifecycle support |
| Local cooperative warning | Managed fleet identities/routes and authenticated peer infrastructure | Uninstrumented traffic, coverage loss, map/reference disagreement and operational rules |
| Manual prototype disconnect | OEM-approved machinery safety design | Hazard analysis, stopping behavior, applicable approvals; not equivalence to service braking |

Industrial changes are a roadmap, not additions to this student's frozen BOM. Named manufacturers do not endorse TARK, and no certification or regulatory approval is inferred from a component specification.
