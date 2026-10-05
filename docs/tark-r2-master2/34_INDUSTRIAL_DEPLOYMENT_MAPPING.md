# 34 — Industrial deployment mapping

Functional roadmap only; it adds no new component to the frozen student BOM.

| Demonstrator | Industrial function / direction | Additional engineering and evidence |
|---|---|---|
| IWR1843BOOST | Qualified rugged radar assembly | Coverage, environmental/EMC/installation diagnostics |
| B0200 | Rugged automotive/industrial camera | Optics/window/cleaning, vibration and mine datasets |
| Lepton/PureThermal | Qualified thermal channel | Lens/resolution/contrast/weather/calibration |
| LG290P rovers/base | Managed localization/corrections | Surveyed datum/map, integrity and outage behavior |
| BNO085 | Vehicle-qualified inertial evidence | Bias/temperature/vibration/magnetic effects |
| Orin dev kit | Rugged SOM/edge computer | Power transients, cooling, lifecycle and timing |
| ESP32 dev board | Appropriate local industrial/OEM controller | Hazard-based architecture, diagnostics, reset/expiry proof |
| Magnetic wheel sensing | Approved OEM speed/CAN/J1939 evidence | Scaling/freshness/slip, initially read-only |
| L298N | OEM-approved propulsion/brake gateway, if later permitted | No arbitrary CAN writes or student direct brake control |
| TT motors | Existing dumper drivetrain | No transfer of model torque/braking/adhesion |
| Local Wi-Fi AP | Site-selected mine communications | RF survey, redundancy/security/latency/loss |
| LCD/buzzer | Cab-qualified HMI/alert | Glare/noise/human factors/nuisance alarms |
| NVMe/replay | Qualified evidence recorder | Power-fail handling/retention/access/integrity |
| Acrylic robot | Existing HEMM platform | Mounting/structural/environmental approval |
| Manual cutoff | Approved machinery safety function | Energy isolation versus service braking distinction |

## Deployment phases

1. SHADOW MODE: observe and record; no driver intervention authority.
2. ADVISORY MODE: approved warnings and navigation, trained operator remains responsible.
3. SUPERVISED PILOT: formal controlled operational evaluation with incident/availability/false-alert evidence.
4. OEM-APPROVED INTERVENTION: only after necessary validation, certification/approval and qualified integration.

These industrial phases are not the R1 software's phase flags; the current prototype remains DISABLED_PHASE_1. Applicable standards and mine regulations require qualified review for the actual equipment/jurisdiction; this document grants no regulatory approval or certification.
