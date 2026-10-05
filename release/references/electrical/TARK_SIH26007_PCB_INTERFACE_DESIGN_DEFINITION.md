# Low-voltage PCB interface design definition

Revision 1.0. Date 2026-09-21.

**PHYSICAL PCB LAYOUT PENDING EXACT COMPONENT AND MECHANICAL VERIFICATION.**

This document defines a possible low-voltage carrier's required continuity. It is not a completed PCB, a new control architecture or a fabrication release. All existing equipment and high-current wiring remain external. No new component, circuit, connector pin number, footprint, protection rating or dimension is introduced.

## Purpose and boundary

A carrier may organize the already-defined logic-level interfaces and regulated logic power. Its only permitted logical nets at this stage are the 15-net subset in `TARK_SIH26007_PCB_LOGICAL_NETLIST.csv` and the workbook's PCB interface tab. Repeated endpoints describe required continuity, not a new wire added to the vehicle schedule.

Exclude N-BAT+, N-BMS+, N-PROTECTED12+, N-TRACTION12+, N-TRACTION-, N-LOGIC12+, PS1-IN-RETURN-HOLD, all four motor power nets, both E-stop supply segments, K1-COIL+/-, suppression and K1-AUX-RAW. No traction current or physical safety-current path is assigned to this board. Do not bridge N-LOGIC-GND to battery/traction/input negative.

## Connector requirements, not connector assignments

| Interface group | Existing allowed signals | Restrictions before pin/pad allocation |
| --- | --- | --- |
| Pi header interface | Pin 2 5V; Pin 3 SDA; Pin 5 SCL; Pin 6/20 GND; Pin 8 TX; Pin 10 RX | Header orientation, mating method and backfeed H06/H23; Pin 1 excluded |
| ESP32 allocated interface | J1-4/5/6/7 encoders; J1-15/16/17/18 PWM/DIR; J1-19 diagnostic; J1-21/22 logic supply/reference | No other J1 allocation; board revision, logic levels and mating layout H20/H23 |
| Radar interface | LD2450 Pin 1 VCC; Pin 2 GND; Pin 3 TX; Pin 4 RX | Electrical levels and connector orientation H16; no connector pitch guessed |
| Thermal sensor interface | SDA, SCL, GND | VCC/VIN, pullups, address and purchased pin identities H09; supply pin remains unassigned |
| IMU interface | SDA, SCL, GND | VCC/VIN, pullups, address and purchased pin identities H10; supply pin remains unassigned |
| Left/right encoder signal interface | A/B; GND only if purchased interface supports it | No VCC, polarity, pullup or output voltage inferred; H07/H08 |
| MDD10A logic header | P1 GND; P2 PWM2; P3 DIR2; P4 PWM1; P5 DIR1 | Logic interface only. T1-T6 are excluded from the board |
| Auxiliary diagnostic | Conditioned ESTOP-AUX-STATUS to GPIO13 | H15 must establish SC1 output/reference compatibility first. No raw auxiliary contact or safety current on board |
| GNSS and camera | External USB cable assemblies to Pi | Not assigned carrier pads, GPIO UART, USB differential traces or power switches |
| Antenna | External ANT1-to-GNSS1 RF assembly | No RF trace, connector or antenna bias circuit designed |
| Pi-to-ESP32 | Existing configured serial software boundary | H26: physical transport/cable unassigned; not an additional copper route |

Physical connector designators, part numbers, pin-to-pad mappings and pitch: **TBD / VERIFY AGAINST PURCHASED PART**. The table names interface groups, not invented physical connector objects.

## Domains and logical signal classes

| Class | Nets | Constraints |
| --- | --- | --- |
| Regulated logic supply | N-LOGIC5+ | Rating/voltage tolerance/powering arrangement and trace capacity require H05/H06. Do not feed sensor VCC merely because it is nearby |
| Logic reference | N-LOGIC-GND | Continuous reference where electrically approved. No cross-domain bond added |
| Shared I2C | I2C-SDA, I2C-SCL | Preserve one shared SDA and one shared SCL node; branch lengths and pullups require purchased modules and bus requirements |
| Radar UART | RADAR-TX, RADAR-RX | Keep crossover; verify purchased signal levels and defined reference before release |
| Controller outputs | ESP-PWM1, ESP-DIR1, ESP-PWM2, ESP-DIR2 | Fixed mappings; no new enable pin or motor authority |
| Encoder inputs | ENC-L-A/B, ENC-R-A/B | Isolate from noisy high-current harnesses where practical; no conditioning components invented |
| Diagnostic only | ESTOP-AUX-STATUS | Logic-compatible conditioned status only; not a primary E-stop implementation |

## Test access requirements

Provide identifiable access to the approved logic reference, regulated logic rail, I2C, UART, four controller-output signals, four encoder signals and conditioned diagnostic status only after the interface is released. These are future access requirements on existing nets, not assigned test-point components or pad coordinates. Access design, loading, probe safety and clearances remain TBD. Do not add a test jumper across E-stop, K1, fuses or ground-domain boundaries.

## Placement and mechanical constraints

- BOARD DIMENSION TBD / VERIFY MECHANICAL DESIGN.
- FOOTPRINT TBD / VERIFY DATASHEET for every connector and mounted module.
- Locate Pi/ESP32 mating interfaces from verified board drawings; do not scale a photograph to infer pitch or mounting dimensions.
- Keep service connectors labelled and accessible; preserve insertion/removal and cable bend space from purchased cable data.
- Separate low-level sensor/encoder interfaces from external motor-current harnesses where practical. Exact clearance, zone outline and keepout dimensions are TBD.
- Mounting-hole count, diameter, location, fastener clearance, enclosure fit and shock/vibration provisions are TBD.
- Retain GNSS antenna/RF and USB assembly constraints from purchased documentation. No on-board antenna layout inferred.

## Routing constraints and release sequence

Use direct digital routes, distinguish I2C/UART classes and preserve approved logic reference continuity. Do not add copper on any excluded net. Numeric widths, clearances, copper weight, layer stack, via rules, maximum currents, impedance requirements and allowable bus lengths require component/load/manufacturing evidence; none are specified here.

Before a physical board is designed: resolve H23-H25 and all interface holds; assign verified connectors/footprints; document pin-to-pad correspondence; compare every board net with the canonical subset; run native schematic ERC and board DRC; review deliberate unconnected pins and domain boundaries; obtain independent engineering approval. Only then can fabrication outputs be considered.

No EMI compliance, functional-safety compliance, production certification or mine certification is claimed. TRACTION = DISABLED_PHASE_1. NO PHYSICAL TRACTION AUTHORIZATION.
