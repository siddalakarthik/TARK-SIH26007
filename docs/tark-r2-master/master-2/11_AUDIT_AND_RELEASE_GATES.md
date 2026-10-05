# Master-2 — audit and release gates

Revision M2-D1 • 1 October 2026 • **SYSTEM-DESIGN HANDOFF; NOT A FABRICATION OR MOTION RELEASE**

## 1. Conclusion

The requested Master-2 system-design scope is covered in this twelve-document package. Master Hardware Freeze 1 remains authoritative and unchanged. This is completion of a design handoff, not evidence that the proposed R2 algorithms, new sensor integration, navigation or fleet functions have already been implemented or physically verified.

The three user-defined boundaries remain explicit: wheel carrier/magnet geometry is pending measurements; GPIO16/GPIO17 are not final motor pins; Jetson regional SKU selection is a purchasing check, not a compute-platform redesign. No additional premium sensor is selected and no reserve is converted into feature spending.

## 2. Scope audit

| Requested area | Design record | Boundary retained |
|---|---|---|
| Complete system architecture | [01](01_SYSTEM_ARCHITECTURE.md) | Local decisions separate from monitoring/cooperation; current and proposed software distinguished |
| Interfaces and communication | [02](02_INTERFACE_CONTROL.md) | Logical interface allocations, timing/provenance and current strict Protocol V2; no invented physical GPIO |
| Power/protection | [03](03_POWER_AND_PROTECTION.md) | Branch/load/protection calculations and return-path review; no unverified fuse, wire, pack or converter rating released |
| Mechanics/calibration | [04](04_MECHANICAL_AND_CALIBRATION.md) | Parameterized dimensions, payload/CG and wheel geometry; measured fabrication details still required |
| Algorithms/operating envelope | [05](05_ALGORITHMS_AND_OPERATING_ENVELOPE.md) | Proposed R2 processing and uncertainty handling; current R1 safety implementation not rewritten |
| Navigation/fleet | [06](06_NAVIGATION_AND_FLEET.md) | Reference-aware RTK/local road graph/cooperative warning; no autonomous-driving or traffic-clearance claim |
| HMI/control room | [07](07_HMI_AND_CONTROL_ROOM.md) | Shared application, truthful provenance and replay separation; browser remains monitoring-only |
| Failure/security/recovery | [08](08_FAILURE_SECURITY_AND_RECOVERY.md) | Twenty-four defined fault cases and explicit capability degradation |
| Validation | [09](09_VALIDATION_PLAN.md) | Twenty-two proposed tests, requirements linkage and G0–G8 gates; not reported as executed tests |
| Feasibility/viability/impact | [10](10_FEASIBILITY_VIABILITY_IMPACT.md) | Conditional integration feasibility and measurable outcomes, not invented percentages or ROI |
| Industrial mapping | [10](10_FEASIBILITY_VIABILITY_IMPACT.md) | Research-to-mine progression separate from the frozen demonstrator BOM |

## 3. Unresolved detail-design and release register

| ID | Required input / decision | Work permitted now | Release prevented until resolved |
|---|---|---|---|
| H01 | Wheel-hub/shaft/mount clearances and actual wheel dimensions | Two 14-bit SPI paths, parametric mounting and response algorithms | Exact carrier/magnet assembly, mounting drawing and calibrated wheel-distance claim |
| H02 | Exact ESP32 PCB/revision/pin evidence and existing connections | Logical MOTOR_IN3/MOTOR_IN4, interface budget and board-review checklist | Final physical assignments, especially GPIO16/GPIO17, and powered motor wiring |
| H03 | Jetson regional purchase SKU, invoice and availability | Orin Nano Super 8 GB architecture and interfaces | Procurement release for exact regional SKU; no architectural redesign required |
| H04 | Battery identity/protection/charger, peak loads and exact power assemblies | Domain topology and load/fuse/conductor-sizing method | Energization drawing, rated parts selection and runtime claim |
| H05 | Actual chassis payload, mass distribution, mounting and enclosure measurements | Layout envelopes, access/thermal/CG checks | Final cut/drill dimensions and a claim that the full payload is safely mobile |
| H06 | Delivered sensor firmware/formats, antenna/reference details and timestamp behavior | Single-owner adapters and acquisition/validation design | Actual acquisition/coverage/latency claims and approved calibration |
| H07 | Board-specific USB/boot identity/scheduler/watchdog evidence and binding | Existing portable Protocol V2 and supervisor software remain the baseline | Physical communication/watchdog verification and future motion-phase release |
| H08 | Reviewed wheel-response communication extension | Define the telemetry requirement and tests through the existing stack | Claim that current V2 STATUS already carries magnetic-wheel feedback |
| H09 | Qualified inference models, characterization data, map/reference and calibration | R2 implementation work packages W2–W7 in shadow/simulation mode | Validated usable-distance, localization integrity, navigation/fleet and full replay claims |
| H10 | Separately approved motion phase, rated interruption and measured response | DISABLED_PHASE_1 operation and software-only tests | Any positive applied motor output or physical stopping-performance claim |

H01–H10 do not authorize new component substitutions. If measured detail cannot fit the frozen design or allocation, raise a documented conflict; do not silently change the platform, protection or budget.

## 4. Important software handoff

The existing authoritative transport is Protocol V2, not legacy V1. Its strict STATUS schema does not include the new wheel-sensing payload. A future wheel-response extension requires explicit review/versioning and coordinated host, firmware, vectors, logging and replay changes through the same communication stack. Do not inject unknown keys into V2 or construct a parallel protocol.

Current R1 software evidence does not establish R2 multi-sensor fusion, calibrated free-space/usable-distance estimation, navigation, cooperative conflict prediction or complete multi-sensor deterministic replay. Those are specified here and listed as future implementation work, not represented as completed features.

## 5. Preservation and checks

This documentation pass checks the twelve M1 files against their pre-edit SHA-256 inventory, local Markdown link targets, package coverage, budget arithmetic and tracked Git differences. It does not rerun historical backend/frontend/firmware suites or convert their historical counts into new evidence.

Results: all **12/12 M1 SHA-256 hashes unchanged**; **12 Master-2 documents present**; **27 local Markdown link targets checked, zero broken**; allocation/total/reserve arithmetic reconciled; no tracked or staged Git differences. Previously untracked work remains present. The documentation review also clarified the HMI zero-speed footnote so it cannot be read as a new phase number.

Budget reconciliation: INR 192,150 electronics + INR 55,000 allocations = INR 247,150 planned additional spending; INR 250,000 ceiling minus INR 247,150 = INR 2,850 unassigned reserve. The allocation subtotal includes its existing spares/price/contingency categories; these must not be counted again as extra available money. Owned acquisition is recorded at INR 0, not declared economically valueless.

Only this new `master-2` documentation directory is authored for this handoff. Existing untracked work is preserved. No application, firmware, configuration, M1 BOM or M1 source document is intentionally edited. No purchases, Git commit/push, COM/USB/I2C access, flashing or physical experiment is performed.

## 6. Next work and release decision

1. Obtain H01/H02/H04/H05 measurements and labels using the existing unpowered evidence workflow; resolve H03 during purchasing only.
2. Convert the parametric power/mechanical design into reviewed as-built drawings when those inputs exist. Do not energize from this package alone.
3. Implement W2–W7 through the existing application/protocol boundaries, initially with deterministic fixtures and shadow operation; request explicit approval for any protocol extension.
4. Execute the staged validation plan with source/configuration/calibration identities and original evidence. Separate software, bench, restrained-model and industrial maturity.
5. Request a separate phase-bound authorization before motion-capable physical testing. Documentation completion does not lift the zero-output boundary.

**Master-2 system-design handoff: COMPLETE. Detailed fabrication/energization release: HOLD. New R2 implementation and physical validation: PENDING.**

Traction remains `DISABLED_PHASE_1`. No GNSS, IMU, thermal, camera, map, peer or browser observation is granted motor authority by this package. No mine certification or guaranteed collision avoidance is claimed.
