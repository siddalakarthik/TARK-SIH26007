# Source register and naming resolution

Revision 1.0. Date 2026-09-21. CONTROLLED DESIGN / PRE HARDWARE COMMISSIONING.

## Authority and reviewed evidence

| ID | Source | Use and limitation |
| --- | --- | --- |
| S0 | Current electrical-package request and subsequent explicit user approval of canonical names | Controls deliverables, no-invention rules, approved C01/C02 resolution and Phase 1 restrictions |
| S0A | User surgical correction request, attachment `a629bb77-dda9-4d0a-8a05-5d75a3a30497/Pasted text.txt` | Renames only the open PS1 input-return stub; separates physical identifier resolution from functional net membership; requires full Pi header, K1 warnings and 20 exact traces. No topology change authorized |
| S1 | `outputs/FINAL_ENGINEERING_PRESENTATION.svg` and matching PDF, REV FINAL - CORRECTED, 2026-09-14 | Highest supplied electrical drawing; all nine zones and pin tables. Conflicting supply labels superseded only as approved below |
| S2 | `outputs/TARK_SIH26007_MASTER_PROJECT_DOSSIER_V1_0.docx` | Current project boundary, GNSS USB, frozen software identity, pre-commissioning maturity |
| S3 | Downloads: `TARK_SIH26007_FINAL_ENGINEERING_MASTER_REPORT_V8 (1).docx` | Supporting project requirements. Older sensor power instruction is explicitly superseded; not authority for a new VCC net |
| S4 | `outputs/TARK_SIH26007_LEGO_STYLE_BUILD_AND_COMMISSIONING_MANUAL_V2.docx` | Supporting assembly and commissioning constraints; not physical evidence |
| S5 | Exact purchased manufacturer documents | No exact purchased BMS, converter, coil driver, contactor, sensor breakout, encoder, connector or mechanical drawing set verified. All affected values remain HOLD |
| S6 | `tark/docs/ESP32_PROTOCOL_V1.md`, `SOFTWARE_FREEZE_BASELINE.md`, `FINAL_SOFTWARE_COMMUNICATION_CLOSURE_REPORT.md` | Software relationships only. Frozen baseline 2d319e7; QA 962365e; tag tark-software-freeze-2026-09-20. Does not establish physical USB, watchdog or electrical compatibility |
| S7 | [Official Raspberry Pi 4 Model B datasheet, Release 1.1, March 2024](https://pip-assets.raspberrypi.com/categories/545-raspberry-pi-4-model-b/documents/RP-008341-DS-1-raspberry-pi-4-datasheet.pdf), Figure 3, printed page 9 (PDF page 10) | Downloaded from Raspberry Pi and inspected as a rendered diagram. Authority only for 40-position header function names; existing TARK SDA/SCL/TX/RX allocations remain from S1. ID_SD/ID_SC stay unallocated. This is not purchased-board verification |
| H0 | `work/tark_sih26007_master_netlist.json` | Historical path lists only; not imported as electrically common nodes across fuses, switches or drivers |

Original files were not overwritten. Source fingerprints and absolute paths are recorded in `SOURCE_FILE_HASHES.json`. Reference S5 in a schedule row is a requirement for verification, not a claim that missing purchased documentation was available.

## C01 - RESOLVED

Conflict found: S1 Zone 1 / Zone 8 and Table 6 used N-TRACTION12+ upstream of K1 while Zone 6 / Table 2 used that same label downstream. Two sides of a series isolation contact must not become one net by label equivalence.

Resolution: explicit user approval on 2026-09-21. K1 MAIN IN is on N-PROTECTED12+. K1 MAIN OUT is on N-TRACTION12+, shared only with MDD10A T3 POWER+. The physical contact and wiring remain unchanged.

## C02 - RESOLVED

Conflict found: S1 Zone 1 assigned N-LOGIC12+ and N-TRACTION12+ to branches of the same F1 output conductor, without an intervening component. The first proposed resolution using N-LOGIC12+ for that common node was not adopted.

Resolution: explicit user approval. F1 OUT, F2 IN, F3 IN and K1 MAIN IN are one node named N-PROTECTED12+. F2 OUT to PS1 IN+ is N-LOGIC12+. No fuse, contact or wire route is added or removed.

| Physical conductor segment | Canonical net | Naming basis |
| --- | --- | --- |
| B1 positive to BMS functional battery input | N-BAT+ | Existing path; exact BMS terminals H03 |
| BMS protected output to F1 input | N-BMS+ | Distinct existing conductor across BMS boundary |
| F1 output to F2/F3/K1 inputs | N-PROTECTED12+ | Explicit user approval |
| F2 output to converter IN+ | N-LOGIC12+ | Explicit user approval |
| K1 main output to U3 T3 | N-TRACTION12+ | Explicit user approval; downstream only |
| F3 output to ES1 NC input | N-ESTOP-FUSED+ | Dedicated existing E-stop fused segment; no upstream alias |
| ES1 NC output to CD1 input | N-ESTOP-SWITCHED+ | Distinct existing switched control segment |
| CD1 output to K1 coil A and suppression | K1-COIL+ | User-approved coil name; physical polarity/terminal marking TBD |
| K1 coil B and suppression return-side | K1-COIL- | User-approved coil name; driver return connection remains unresolved |
| B1/BMS negative and U3 T4 | N-TRACTION- | Source drawing common-node intent; purchased BMS topology H03 |

N-BAT- is not added as an alias of the same N-TRACTION- conductor. K1-TRACTION+ is not added as an alias of N-TRACTION12+. Cable names GNSS-USB, CAMERA-USB and GNSS-ANTENNA designate assemblies, not single copper nets.

## C03 - historical instruction superseded, no new decision required

S3 contains an older instruction to power the MLX90640/BNO055 sensors from Pi Pin 1. S1 and the current user's explicit pin requirement prohibit external power on Pi Pin 1 and leave purchased sensor VCC/VIN unresolved. The current explicit instruction controls: Pi Pin 1 has no external connection. No sensor supply is assigned. This is a recorded supersession, not an inference of a breakout voltage.

## Source-to-database checks

- Series devices have separate functional input/output terminals. The historical JSON path list is not treated as one net.
- Pi, ESP32, MDD10A, radar and encoder controlled allocations are checked independently in the exported-artifact audit.
- All 22 ESP32 J1 positions are shown. Positions not allocated by the current request are UNALLOCATED / DO NOT CONNECT, without inventing their GPIO identities.
- The existing suppression and auxiliary conditioning boxes have references D1/S1 and SC1 for traceability only. These are not newly introduced circuits or parts.
- No BMS internal protection circuit, coil driver circuit, auxiliary excitation, sensor supply, return bridge, connector pitch or physical footprint is inferred.

No unresolved naming conflict remains. Purchased-part uncertainties remain explicit holds, not electrically completed connections.

## Rev 1.0 surgical correction record

- C01 and C02 remain RESOLVED without change to their approved memberships.
- The former unresolved input-return name `N-LOGIC12-` is superseded by **PS1-IN-RETURN-HOLD**. It contains only PS1 IN- and is not a conductor to another device. PS1 OUT- remains on N-LOGIC-GND, without an input/output or traction-return bridge.
- N-LOGIC-GND has five resolved physical identifiers: U1 Pin 6, U1 Pin 20, U2 J1-22, U3 P1, LD2450 Pin 2. The two sensor grounds and two encoder grounds are HOLD / PHYSICAL PIN VERIFY. PS1 OUT- remains a functional source with purchased terminal identity HOLD, not a sixth resolved terminal.
- Each functional I2C node retains one Pi endpoint and two sensor endpoints. Only the Pi physical identifier is resolved. Sensor SDA/SCL pin numbers remain TBD / VERIFY.
- The complete 40-position Pi table adds 32 UNALLOCATED / DO NOT CONNECT documentation rows, no electrical connections. Original Pi Pin 1 NO EXTERNAL POWER remains unchanged.
- K1 COIL A / COIL B / MAIN IN / MAIN OUT remain functional interfaces. Purchased terminal numbering and coil/driver/return/suppression details must be verified before energization. DESIGN HOLD — DO NOT ENERGIZE.
- Baseline comparison uses the preserved original `TARK_SIH26007_ELECTRICAL_REV1_0.zip`. The corrected archive is separately named; the original source schematic and unrelated project files are unchanged.
