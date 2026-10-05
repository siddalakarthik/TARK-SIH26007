# TARK R2 — clean-sheet flagship research architecture

HISTORICAL R2 design recommendation. Retained as design lineage, not current
R3 as-built authority or commissioning proof. Current software status and gates:
`docs/R3_REASONING_REPORT.md` and `docs/TARK_RELEASE_INDEX.md`.

Revision F0 · 2 October 2026 · Architecture recommendation, not a fabrication or purchase release

## Decision

Build a **removable, instrumented driver-assistance pod on a purpose-built manually moved research cart**, supported by a physically separate cooperative GNSS node and a shared local RTK base/control-room station.

This is a sensing, localization, navigation and fleet-intelligence demonstrator. It is **not an autonomous robot, automatic-braking demonstrator or certified vehicle protection system**. The cart is deliberately human-operated. Its independent mechanical stopping arrangements protect the experiment; the research software does not.

The old acrylic robot, TT motors, L298N, batteries, switches, relay, wheel geometry and GPIO assignments contribute **no design constraints and no parts to this BOM**. Nothing needs to be measured on that robot to progress this architecture.

## Main selections

| Function | New recommendation |
|---|---|
| Main compute | New Raspberry Pi 5 8 GB + official Hailo-8 AI HAT+ 26 TOPS; active cooling |
| Front radar | TI IWR6843ISK, current standalone-capable revision; not the earlier IWR1843BOOST |
| RGB | Arducam B0200, reselected for documented Linux UVC and compressed video |
| Thermal | FLIR Lepton 3.5 + GroupGets PureThermal 3, reselected for an accessible acquisition path |
| Positioning | Three Waveshare LG290P kits: rover A, cooperative rover B, fixed base |
| Motion | BNO085 + two AMT102-V incremental measurement-wheel encoders |
| Mobile support | New custom braked instrument cart; removable rigid sensor pod |
| Power | Enclosed EcoFlow RIVER 2 India-voltage unit + manufacturer power supplies; no loose-cell battery construction |
| Driver interface | Dedicated 7-inch HDMI touch panel and audible indicator |
| Fleet demo | Separate GNSS/Wi-Fi node; no second full perception stack purchased |
| Shared infrastructure | Local AP, base receiver, laboratory laptop/control-room access, test fixtures |

Published hardware capability is not measured TARK performance. Hailo model compilation, USB stream formats, radar firmware/profile and all mounted-system performance remain integration gates.

## Budget

The reset references the approved budget without restating it. This package uses the **INR 250,000 ceiling recorded in the latest Master-1 budget**, not the superseded INR 60,000 early prototype discussion.

| Allocation | INR |
|---|---:|
| Equipment, fabrication and access allowances | 231,950 |
| Unspent price/integration reserve | 15,000 |
| Total planning allocation | 246,950 |
| Further unallocated headroom | 3,050 |

This is a conditional planning budget, not a supplier quote. It includes a limited **laboratory laptop/access allowance, not purchase of a new control-room PC**. Required lab instrument access is similarly disclosed. If those resources are unavailable, reconcile replacement costs before ordering. No premium additions are assigned to the reserve.

## Read in this order

1. [System architecture and demonstration domain](01_SYSTEM_ARCHITECTURE.md)
2. [Exact parts, quantities, specifications and budget](02_COMPONENTS_AND_BUDGET.md)
3. [Alternatives, competitor evidence and source ledger](03_DECISIONS_AND_SOURCES.md)
4. [Interfaces, physical layout, power and protection](04_INTERFACES_POWER_MECHANICS.md)
5. [Validation, industrial scaling and unresolved release gates](05_VALIDATION_SCALABILITY_AND_GATES.md)

## Scope and maturity

The user's scope-reset prompt supersedes earlier flagship hardware authority. Previous Master-1/Master-2 files are preserved unchanged as research history. Their old pin maps, power nets, drivetrain, wheel-sensor assembly assumptions and freeze verdicts do not authorize construction of F0.

This work creates architecture documents only. It does not port software, purchase equipment, contact suppliers, probe hardware, energize components, flash firmware or enable traction. The existing repository's Phase-1 control restrictions are not changed.

**Architecture recommendation complete; fabrication freeze not passed.** Open facts are enumerated rather than concealed behind exact-looking part numbers or dimensions.
