# Owned hardware: photo/measurement required

Revision A0, 1 October 2026. Latest user reply retained as preliminary inventory evidence U02. No physical inspection or powered test was performed in this task. Future evidence must update the same records and add a dated change record; it must not erase the original report.

| Record / BOM | Current user-reported evidence | Unpowered photo/record needed | Freeze consequence |
|---|---|---|---|
| P01 / A16 | ESP32-S3 N16R8 / HW678-style; previous programming identified ESP32-S3 QFN56 rev v0.2, 8 MB PSRAM | Both PCB faces, silkscreen/revision, module markings, header labels and purchase link | MCU identity does not establish PCB pinout, USB wiring, flash size or regulator ratings |
| P02 / A18 | One L298N module drives four TT motors; ENA/ENB jumpers fitted; onboard rail reportedly about 5.00 V | Both board faces, regulator/diode/IC markings, jumper legends, terminal labels and supplier specification | Channel loading, input compatibility, cooling and regulator topology remain unverified |
| P03 / A19 | Four yellow TT geared motors operate on current chassis | Labels/purchase reference; shaft faces, accessible rear shafts, mounting-hole spacing and gearbox dimensions | Gear ratio, rated voltage, RPM, stall current and encoder fit remain unknown |
| P04 / A21 | Pack reportedly measured about 7.78 V | All labels, cell/pack construction visible without opening, connector and charger labels, protection/BMS evidence | No chemistry, capacity, series count or charging voltage inferred |
| P05 / A22 | Separate 12 V SLA reportedly about 1.3 Ah | Full label, model, terminal dimensions and charger specification | Capacity and condition not verified; no runtime inferred |
| P06 / A24 | USB webcam streams successfully on working Pi | Model label, purchase link and saved device information if already available | Working stream does not identify sensor, lens or manual controls |
| P07 / excluded relay | JQC-3FC/T73 DC12V bare relay | All case markings, manufacturer logo and underside pin layout; matching manufacturer datasheet | No assumed pinout or DC interruption rating; excluded from rated cutoff chain |
| P08 / excluded switch | Red two-terminal switch/pushbutton | Body markings, contact/action type, manufacturer/model and rating | Not accepted as a rated traction cutoff |
| P09 / A20 | Clear acrylic four-wheel chassis | Overall length/width, wheel diameter/width, ground clearance, axle/shaft dimensions, mounting-hole spacing, unobstructed deck area | No encoder or premium-electronics mounting fit declared |
| P10 / A15, A23 | Pi 3B+, working OS/Wi-Fi/camera; SanDisk Ultra 32 GB microSDHC A1 | Pi identification and card face/part markings; existing PSU label | Reuse for node B identified; precise asset/PSU/card record remains open |
| P11 / A17 | HLK-LD2450 owned | Front/back revision/label and cable identity | Retained bench comparison asset, not premium primary radar |
| P12 / A25 | Current development computer exists; control-room/base-host role proposed | Host identity, available USB/Wi-Fi, permission to allocate it for base/HMI trials | Do not assume a second laptop or free rental |

## Reported wiring retained, not changed

| Existing ESP32 signal | Existing L298N signal |
|---|---|
| GPIO4 | IN1 |
| GPIO5 | IN2 |
| GPIO16 | IN3 |
| GPIO17 | IN4 |
| GND | GND |

ENA and ENB jumpers are reported installed. This is an evidence record, not a new wiring instruction or proof of safe default output state. The L298N 5 V rail must not supply Pi or ESP32. Old Pi4/MDD10A pin assignments must not overwrite this separate TT/L298N inventory.

## Delivery record

City: Hyderabad, Telangana, India. Target: 15 October 2026. The supplied PIN text was `[MY ACTUAL 6-DIGIT DELIVERY PIN]`, not an actual PIN. Freight/serviceability and delivered-by dates cannot be confirmed from that placeholder. No address was entered into a checkout, no vendor was contacted and no order was placed.

Only unpowered evidence is requested now. Stall-current measurement, battery opening, energized probing and charging experiments are not authorized by this request.
