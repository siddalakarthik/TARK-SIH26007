# 31 — Feasibility

## Technical

Frozen sensors and host interfaces are documented: TI processed USB-UART; RGB UVC; complete thermal USB bridge; SPI IMU/wheel design; GNSS base/two rover architecture; one GPU edge host; local network and storage. Existence is not interoperability or performance proof. The combined timing/power/thermal/USB/payload workload remains measured integration work.

Primary risks: camera exposure/near focus; radar profile/coverage; Lepton FFC/contrast; RTK common reference/multipath; time alignment; unknown wheel geometry; paired TT/L298N demand; actual chassis payload; unique boot identity and physical expiry binding. Every risk has a gate in [45](45_OPEN_ISSUES_REGISTER.md), not a secret replacement component.

## Implementation

Start with deterministic fixtures, acquisition contracts and replay, then sensors individually, then stationary integration. Reuse the actual backend/frontend/portable protocol, not a new application. No main perception burden is placed on Pi 3B+. Extend normalized paths with explicit versions; do not reuse BNO055/MLX90640 drivers as BNO085/Lepton implementations merely because UI labels are similar.

One Jetson's capability must be measured under simultaneous decode/inference/recording/HMI and failures. Module TOPS and NVMe advertised speed are not an application timing result. If required deadlines fail, reduce optional work within the architecture and explicitly narrow test scope; a hardware substitution needs CR evidence.

## Budget and timeline

M1: INR 192,150 electronics + INR 55,000 integration/assemblies/reserves = INR 247,150; INR 2,850 remains unallocated reserve. Owned acquisition is zero additional cost, not zero economic value. R02/R03 must fund actual qualified power/mount assemblies; final quotes and regional SKU price remain unknown. No new premium sensors.

The 4 October submission and 15 October hardware target mentioned earlier are distinct from design completion. No guaranteed delivery or full physical validation date is asserted. Demonstrate only evidence ready by the event; clearly labelled simulation/replay is preferable to fabricated live claims.

## Industrial

Development boards/consumer AP/acrylic model are not production hardware. Industrial progression needs OEM/site hazard analysis, rugged power, EMI/EMC, vibration/environmental assessment, field coverage, map maintenance, human factors and operational trials. Prototype feasibility is conditional and testable; mine deployment feasibility is not established by this package.
