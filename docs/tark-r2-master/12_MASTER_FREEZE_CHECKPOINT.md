# TARK R2 — Master Hardware Freeze 1 checkpoint

HISTORICAL / SUPERSEDED planning branch, not current R3 equipment authority.
Retained without rewriting its original verdict. See `docs/TARK_RELEASE_INDEX.md`.

Revision M1 • 1 October 2026.

## Verdict

**MASTER HARDWARE FREEZE 1: PASSED — technical planning scope only.**

The major categories and exact main components are decided, no optional sensor list remains, the planning total is **INR 247,150 <= INR 250,000**, and the architecture can proceed to Master Prompt 2 without reopening its sensing/compute/localization choices. The expressly permitted wheel-geometry and power-category handoffs remain detail-design work.

This is **not** a procurement, wiring, physical commissioning, software-integration, safety-certification or mine-deployment release. It does not retrospectively pass the earlier Batch-A procurement freeze. The price, regional-SKU, as-built identity and measured-performance limits below are part of this technical verdict, not footnotes to be discarded.

## Final audit

| Check | Result / supporting evidence |
|---|---|
| Every sensor answers an SIH requirement | YES at design level; R01–R07 in document 02 |
| Avoid unnecessary sensor duplication | One premium front radar/RGB/thermal/IMU; two wheel channels; three GNSS receivers have distinct A/B/base roles. Owned bench sensors do not add coverage claims |
| Primary radar geometry | Documented configurable IWR1843BOOST processing/interface selected; actual useful range/angle/velocity remains characterization work |
| Complete thermal acquisition | Core 500-0771-01 + PURETHERMAL-3 + data cable + host/power allocation included |
| RGB appropriateness | Exact fixed-lens B0200/UVC selected; 100-degree diagonal, not horizontal. Manual exposure preference is unresolved and recorded, not claimed satisfied |
| Precise navigation/fleet foundation | Two RTK-capable rovers and local base, antennas, corrections link and second physical node selected; no promised centimetric integrity |
| IMU justification | SPI BNO085 complements location/motion; it does not duplicate metric radar range or replace GNSS indefinitely |
| Motion feedback | Two magnetic angle sensing paths with 100 Hz design target; assembly SKU deferred only to measured hub envelope |
| Compute suitability | One 8 GB GPU developer kit is an appropriate proposed workload class. Concurrent latency/FPS/memory/thermal results are not established |
| Storage sizing | 500 GB plus explicit compressed-retention example and bounded recording requirement; no raw-video endurance claim |
| Local communication | AP + main-node Ethernet + Pi/laptop Wi-Fi covers selected research topology; RF coverage and p95 latency require tests |
| Power/protection accounted for | INR 18,000 category allocation; electronics independent of L298N rail; physical disconnect independent of software |
| Mounts/calibration/test accounted for | Separate mechanical, harness, calibration, aerosol and spare allocations; not consumed by sensor list |
| Competitor overlap analysis | Completed to accessible evidence limit: ten links, prior-description evidence marked D-R, unknowns preserved. No new frame-by-frame verification |
| Differentiation | Ten falsifiable system behaviors mapped to hardware/evidence in document 08; no exclusive novelty claim |
| Budget reconciliation | 38 BOM records, 27 fields; new exact/bundled allocation 192,150 + category/reserves 55,000 + owned 0 = 247,150; headroom 2,850 |
| Optional category removed | Explicit INCLUDE through selection tables or EXCLUDE through document 07; no undecided premium add-on list |
| Exactness sufficient for Prompt 2 | Main selected boards, camera optics, core/bridge, kits and roles fixed. Detailed ratings/pins/geometry remain explicitly assigned to Prompt 2 |
| Prior artifacts and frozen source preserved | New documentation package and external artifact helper only; no application/firmware/PPT edit, commit, push, purchase or physical access |

## Open facts that must stay open

1. **Jetson region:** M1 selects exact 945-13766-0000-000. NVIDIA maps India/Taiwan to 0007, not 0000. M1 does not certify Indian regional compliance, warranty or mains accessories for 0000. Resolve before purchase/use; any SKU/cost change must be recorded explicitly. Electrical architecture need not be reinvented to perform that review.
2. **Owned board/drivetrain:** ESP32 PCB and pins, L298N board limits, TT motor ratings, batteries/chargers and payload are not verified. GPIO16/17 are under investigation. User-reported movement and timeout do not establish that the currently frozen reviewed firmware drove it.
3. **Wheel geometry:** obtain a dimensioned left/right wheel-hub mounting-envelope drawing with shaft/hub diameter, axial/radial clearances and sensor/magnet gap/alignment. Select the exact carrier/magnet assembly within the frozen magnetic SPI direction only after that evidence.
4. **GNSS RF:** the exact kits include active antennas; independent antenna SKU, bias/connector detail, supported antenna bands and phase-center calibration are not established here. Do not infer all-band antenna performance from the receiver's bands or inject external bias.
5. **Power and mechanical detail:** define exact protected converters/battery/charger/cutoff/fuse/connector selections, grounding and inrush. Verify payload/center of gravity before mounting the whole research stack on the acrylic robot. Do not treat a design budget as an energization instruction.
6. **Camera/interface behavior:** horizontal FOV, manual controls, actual UVC modes, thermal radiometric handling/FFC and display EDID require bench characterization.
7. **Software maturity:** new R2 radar/Lepton/BNO085/RTK-correction/magnetic-wheel integration is later work. No code was changed and no new system function was claimed implemented. Current Phase-1 disabled authority is preserved.
8. **Performance/mine limits:** all usable domains await experiments. No HEMM braking, production gain, all-weather detection, certified E-stop or mine certification is claimed.
9. **Cost confidence:** allocations include specified reserves but are not landed quotes. A sufficiently large cost rise requires explicit reconciliation, not substitution with weaker hardware or removal of protection.

## Master Prompt 2 handoff

Proceed with functional and then detailed electrical/mechanical architecture around this component list. Do not re-open the primary radar/RGB/thermal/RTK/IMU/compute selections merely to add more sensors. First establish as-built identity/geometry and safe power requirements; then produce pin reservations, protected branch sizing, interface/connector/net tables, harness and mount drawings, and commissioning gates. No powered instruction should cross an unresolved rating/identity gate.

Preserve single-antenna heading limits, wheel response versus ground speed, time/quality provenance, separate local/cooperative failure effects and independent physical interruption. New software development requires its own authorized task. No hardware access is required or performed for this checkpoint.

## Package and verification

| File | Purpose |
|---|---|
| `01_COMPETITOR_CAPABILITY_MATRIX.md` | Ten requested links, accessible evidence boundaries and overlap |
| `02_TECHNICAL_REQUIREMENTS.md` | SIH requirements and authority limits |
| `03_EXACT_COMPONENT_FREEZE.md` | Exact primary choices, owned exceptions and technical source register |
| `04_FINAL_TECHNICAL_BOM.csv` | Full component-freeze fields, planning costs and provenance |
| `05_COMPONENT_DECISION_LOG.md` | Alternatives, explicit changes and rationales |
| `06_SENSOR_PERFORMANCE_TARGETS.md` | Published/target/measured distinction and experiments |
| `07_COMPONENT_EXCLUSIONS.md` | Binary decisions, no optional category |
| `08_TARK_DIFFERENTIATION_MAP.md` | System behaviors and falsifiable evidence |
| `09_BUDGET_ALLOCATION.md` | Arithmetic, price anchors, uncertainty and retention sizing |
| `10_INTERFACE_SUMMARY.md` | Ports, hosts, data paths and power-category handoff |
| `11_INDUSTRIAL_MAPPING.md` | Demonstrator functions versus industrial qualification |
| `12_MASTER_FREEZE_CHECKPOINT.md` | This audit, limits and handoff |

BOM checks performed: all IDs unique; all requested fields populated with explicit unknowns where appropriate; quantity × rate reconciled independently; recalculation dependency tested and restored; formula-error scan clean; CSV round-trip preserved headers/rows/total/SKU; representative rendered identity/cost and budget ranges inspected. CSV is a values-only table, not a formatted workbook. These are document/arithmetic checks, not hardware/software validation tests.
