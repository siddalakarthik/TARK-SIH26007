# Next physical phase — gated handoff, not authorization

Current release remains `DISABLED_PHASE_1`. No commissioning or wiring is
performed by this document. Each future gate requires a named reviewer,
dated procedure, exact part/configuration identity, raw evidence, result and
explicit approval to proceed. A software pass does not close a physical HOLD.

| Gate | Required work/evidence before acceptance | Current boundary |
|---|---|---|
| A — Purchased parts | Manufacturer, variant/revision, markings, connector orientation, controlled datasheets and receipt photos | HOLD / VERIFY; no identity inference from a port name |
| B — Electrical HOLD closure | Resolve H01–H27 against the controlled netlist, ratings, protection, return topology and independent inspection | No energization or PCB fabrication release |
| C — Sensors | Approved isolated bench plan; actual radar frames, GNSS checksum-valid fixes, UVC frames, BNO055/MLX90640 samples, timestamps/dropouts/calibration | Mocked/software coverage is not sensor evidence |
| D — ESP32 board binding | Reviewed RX/TX, unique-per-boot identity, serialized RX/tick/disconnect hooks, scheduling, SDK/board build and disabled status | app_main remains UNAVAILABLE_HARDWARE_BINDING_PENDING |
| E — Physical watchdog | Register/test actual watchdog, reset/freeze/disconnect behavior and timing with outputs isolated | Board-neutral supervision is not hardware watchdog verification |
| F — E-stop/contact isolation | Approved power-off checks then controlled coil/contact tests, measured isolation and manual-reset behavior; aux status remains diagnostic | Coil/driver/return/suppression/contact ratings under HOLD |
| G — Low-speed vehicle | Separate traction authorization after A–F; secured test area, operator, restraints, stop procedure, reviewed configuration and risk assessment | R1 contains no traction enable |
| H — Encoders | Supply/interface, counts/revolution, polarity, wrap, missing/invalid pulses and commanded-versus-wheel response | Wheel response is not ground speed |
| I — Braking/deceleration | Repeatable braking measurements under defined load, surface, grade and actuator conditions, including dispersion | 0.5 m/s² is a parameter, not a measurement |
| J — Stopping distance | Measure latency, reaction/stopping distances with independent reference instruments under declared conditions | Software formula alone cannot authorize speed |
| K — Fog/degraded visibility | Characterized visibility, independent ground truth, target classes, dropout/false-return records and repeatable conditions | Synthetic degradation is not fog testing |
| L — Perception envelope | Calibrate usable sensing extent/uncertainty and corridor relevance from measured data, including empty-scene semantics | Nearest-track D_env is not free-space verification |
| M — Physical PV-SOE | Review model adequacy; introduce measured limits through change control; repeat software and approved physical tests | No guarantee, certification or autonomy implied |

Permanent restrictions (including Pi Pin 1 NO EXTERNAL POWER and unallocated
pins DO NOT CONNECT) remain restrictions; “HOLD closure” never authorizes
reassigning them. Resolve only reviewable unknowns through approved design control.

References: [HOLD register](../release/references/electrical/HOLD_REGISTER.md),
[electrical resolutions](../release/references/electrical/SOURCE_REGISTER.md),
[Protocol V2](ESP32_PROTOCOL_V2.md), [firmware limitations](../firmware/esp32/KNOWN_LIMITATIONS.md).
No fuse value, sensor/encoder supply, wire gauge, coil rating or PCB fabrication
dimension is invented. Future work belongs on a separately authorized branch.
