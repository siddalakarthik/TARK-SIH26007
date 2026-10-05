# TARK R2 — Hardware Freeze Batch A checkpoint

HISTORICAL / SUPERSEDED planning branch. Retained for traceability, not current
R3 hardware or software authority. See `docs/TARK_RELEASE_INDEX.md`.

Revision A0. Evidence date: 1 October 2026. **Review package complete; hardware freeze not achieved. Not released for ordering, wiring or energization.**

## System identity and scope

Small moving research robot representing a future industrial retrofit assistance concept. Primary review selections: IWR1843BOOST; Arducam B0200; Lepton 3.5 500-0771-01 plus PURETHERMAL-3; Jetson 945-13766-0007-000; three Waveshare 33000 GNSS kits (two rovers/one base); Waveshare 11199 HDMI display; Kingston SNV3S/500G; UH720 V5.0; WR902AC V3. Exact selected accessory identities and quantities are in H2/CSV.

Pi 3B+ is node-B positioning/correction relay only. LD2450 and existing webcam are bench references only. ESP32 is the later local supervisory endpoint; L298N/TT motors remain the existing drive under assessment. No verified encoder, mobile electronics supply or independent cutoff selection exists. LTE and premium motor upgrade are EXCLUDED.

No application, firmware, R1 evidence or submitted PPT was changed. No hardware was accessed, no electrical test performed, no purchase made, no supplier or rental agreement concluded. Current robot motion remains team-reported and separate from frozen R1 zero-output evidence.

## Cost gate

- Purchase commitment made in this batch: **INR 0**; prior spend unaudited.
- Observed-price electronics subset: **INR 184,449.64**; not a landed or committed total.
- Protected integration allowances: **INR 45,000**.
- Partial scenario including reserves: **INR 229,449.64**.
- Additional-expenditure ceiling: **INR 205,000**.
- Partial scenario excess: **INR 24,449.64**, before unpriced A13/A14 and unresolved taxes/freight.
- Ceiling room after listed subset: **INR 20,550.36**, insufficient for protected reserves.
- Full new purchase cost and compliant H4–H12 remaining budget: **UNKNOWN / NOT ESTABLISHED**.

## Release-blocking evidence

| Gate | Missing evidence / exact next closure action | Owner/input |
|---|---|---|
| G01 Owned identities | P01–P12 unpowered photos/labels/measurements; verify ESP32 PCB, bridge, motors, pack, SLA, chassis/wheels/shaft, switch/relay and reference assets | Team evidence; do not guess |
| G02 Wheel sensing | Select one fit-verified dual-side directional sensing solution; resolve occupied GPIO4/5/16/17 against exact board | Geometry + board identity, then component/interface review |
| G03 Mobile power and cutoff | Select compatible protected electronics energy source and rated independent traction interruption, based on actual loads/pack/payload | Identity/load/geometry evidence; detailed H5/H6 follows only after category/feasibility closure |
| G04 Exact purchased assembly | Manufacturer board/antenna details for GNSS; delivered AP/hub revisions; display mode/accessories; unpriced data/video links; unresolved size/mass/current fields | Manufacturer and exact supplier documentation |
| G05 Budget | Reconcile exact-SKU all-in quotes or documented loans within 205,000 while retaining adequate integration reserves | Supplier evidence and explicit change control, not removed safety provisions |
| G06 Procurement | Actual six-digit Hyderabad PIN and evidence of available complete parts by 15 October; three GNSS kits currently listed out of stock | Team PIN plus supplier dispatch/arrival confirmation; same-part lab loan/rental if confirmed better |

There are **three unresolved mandatory exact selections** (GAP-ENCODER, GAP-POWER, GAP-CUTOFF) plus identity, compatibility and sourcing gates. This is not a zero-hold BOM.

## H1/H2/H3 consistency and adversarial audit

| Check | Result |
|---|---|
| 35 requirements have component/reserve/test or explicit gap allocation | Traceability present; gaps are not requirements satisfaction |
| All A01–A26 items have H1 linkage and H3 function/one authority class | Documented; passive parts gain no command authority |
| R01–R08 reserve functions are allocated | Documented allowances, not invented physical parts |
| Every required H3 function has a selected item | FAIL: wheel sensing, mobile source and cutoff unfilled |
| Compute/communication duplication | Roles separated; no extra Jetson/MCU/LTE/LoRa selected |
| Host interfaces and mandatory acquisition chain | Concept traced; exact accessory/revision/power closure incomplete |
| Radar debugger/capture requirement | Onboard XDS110 identified; no raw-ADC requirement, DCA1000 excluded |
| Thermal assembly | Core plus bridge plus explicit cable, not core-only costing |
| GNSS completeness | Base/two rovers/three antennas accounted; exact antenna match and availability NOT closed |
| Encoder fit and drive current | FAIL: physical geometry and motor/bridge identities not established |
| Price versus landed cost | Distinct; UNKNOWN values not converted to zero |
| Budget and 15 October delivery | FAIL: partial scenario over ceiling and delivery not committed |
| Owned components and false industrial claims | Verification register and claim matrix present; no new physical verification claim |
| Excluded hardware | Separate exclusion register; no active role assigned to excluded devices |

## Artifact verification

The generated CSV contains 34 records (26 physical-item rows and 8 explicitly labelled allowances), with 38 fields. Listed-price extensions were calculated and reconciled to 184,449.64; reserves reconcile to 45,000. Unpriced A13/A14 extensions remain UNKNOWN. CSV reimport and a formula-error scan passed. The three rendered selection/owned/reserve ranges were visually inspected. These are data/layout checks only, not hardware qualification.

## Package and resumption point

Required outputs: H1_HARDWARE_REQUIREMENTS.md, H2_FINAL_BOM.md, FINAL_BOM.csv, H2_COMPONENT_DECISION_LOG.md, H2_EXCLUDED_HARDWARE.md, H3_COMPONENT_FUNCTION_MATRIX.md, HARDWARE_CLAIM_MATRIX_A.md, BATCH_A_SOURCE_LEDGER.md, BATCH_A_CHANGE_LOG.md and this checkpoint. PHOTO_MEASUREMENT_REQUIRED.md is the additional evidence request register.

Resume by updating the specific P/BOM records with new evidence and CR-A entries. Obtain actual PIN/quotes before asserting landed costs. Re-audit G01–G06 before any PASS; do not silently move unselected mandatory hardware into H4/H5/H6. Batch-A artifact checks are documentation checks, not firmware/software regression or physical validation.

BATCH A FREEZE: FAILED
