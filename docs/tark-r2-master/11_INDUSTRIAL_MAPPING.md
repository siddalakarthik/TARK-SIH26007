# TARK R2 — demonstrator to industrial function

Revision M1 • Function mapping is not a parts-for-parts HEMM retrofit prescription.

| Research component / behavior | Industrial function represented | What changes for a real mine vehicle | Evidence needed before any operational claim |
|---|---|---|---|
| IWR1843BOOST front sensing | Obstacle geometry / relative motion | Ruggedized approved radar placement, coverage redundancy and EMC/environmental assessment | Target-class/weather/road-condition coverage and false/missed warning rates |
| B0200 RGB | Scene semantics, signs and contextual awareness | Industrial camera/cleaning/window, vibration/lighting qualification | Mine-specific dataset, calibration maintenance and domain-shift performance |
| Lepton/PureThermal | Complementary LWIR contrast | Rugged complete camera with suitable resolution/lens/window/cleaning | Thermal contrast versus target distance/weather, association and failure modes |
| LG290P base/two rovers | Vehicle tracking, mine-route guidance and cooperative fleet state | Surveyed mine datum/map, correction infrastructure, coverage and integrity monitoring | Localization error/availability near pits and cliffs; stale/wrong-reference behavior |
| BNO085 | Vehicle angular/motion evidence | Vehicle-qualified inertial source, mounting and temperature/EMC characterization | Bias/drift, vibration, magnetic contamination and fusion consistency |
| Two magnetic wheel pickups | Wheel-response plausibility | Approved OEM CAN/J1939 speed/motion source or approved independent measurement; read-only by default | Signal definitions, wheel slip, scaling, freshness and OEM integration approval |
| Orin Nano developer kit | Local edge perception/evidence processing | Industrial compute, protected vehicle power, thermal/environmental design and lifecycle support | Worst-case timing, availability, cybersecurity and fault containment |
| ESP32 endpoint | Local bounded-command/supervisory interface concept | Appropriate OEM/safety controller only after hazard analysis; no presumption ESP32 is certified | Independent fault handling, safety lifecycle, restart/timeout behavior and interface approval |
| L298N + TT + acrylic chassis | Physical request/response and loss-of-command demonstration | **Not a representation of dump-truck torque, mass, adhesion or brake dynamics** | No extrapolation from model stop distance to HEMM |
| Local screen + buzzer | Driver warning and explainability | Cab-qualified HMI/acoustics, human-factors and alarm-priority design | Operator comprehension, workload, nuisance rates and response times |
| Consumer NVMe + replay | Event/evidence recorder | Qualified power-fail handling, retention, clock integrity, access control and maintenance | Recoverability, completeness and chain of evidence |
| Wi-Fi/AP and two physical nodes | Cooperative state/correction transport | Mine Wi-Fi/private LTE/5G/approved V2X depending survey and requirements | Latency/loss/coverage, authentication, interference and infrastructure failure |
| Independent manual traction disconnect | Prototype physical energy-removal concept | OEM-approved machinery safety architecture; electrical cutoff is not automatically service braking | Hazard/risk analysis, stopping behavior and applicable compliance evidence |
| Controlled aerosol experiment | Repeatable adverse-observability characterization | Controlled representative mine trials across fog, rain, dust and terrain | Independent test protocol, baseline, confidence intervals and operational limits |

## Operational outcomes: hypotheses, not percentages

SIH26007 asks for fewer collisions, improved haulage/cycle time, fleet utilization, continuity and production. The demonstrator can collect evidence availability, localization error, warning lead time, latency and controlled-route task results. It cannot establish mine-wide production improvement or accident-rate reduction from a short student trial.

The industrial pathway is: requirements and hazards → verified sensing/coverage → validated vehicle/road models → operator-assistance trials → approved integration → operational evaluation. No autonomous traction or brake retrofit is authorized by this hardware freeze. Local monitoring can be useful well before any motion intervention is justified.
