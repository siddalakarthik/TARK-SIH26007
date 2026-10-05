# TARK R2 — Master-2 system design handoff

Revision M2-D1 • 1 October 2026 • **DESIGN PACKAGE — NOT AS-BUILT OR ENERGIZATION RELEASE**

## Decision

Proceed with the Master Hardware Freeze 1 component platform. This package completes the system-level architecture and defines the remaining measured-detail gates. It does not modify the frozen software, claim new algorithms are implemented, or invent the facts needed for a fabrication-ready electrical/mechanical release.

### Three controlling clarifications

1. **Wheel sensing:** exactly two 14-bit SPI magnetic-angle sensing paths. Carrier, magnet and mounting assembly remain unassigned until the left/right wheel-hub envelope is measured. No assumed motor shaft or wheel diameter.
2. **Motor GPIO:** retain reported GPIO4→IN1 and GPIO5→IN2 as preliminary as-built evidence. Define `MOTOR_IN3` and `MOTOR_IN4` logically. **GPIO16/GPIO17 remain under physical investigation and are not final assignments.** This package makes no new physical GPIO assignment.
3. **Compute region:** the frozen platform is **NVIDIA Jetson Orin Nano Super 8 GB developer kit**. 0000 versus India/Taiwan 0007 is a later purchasing/region check. It does not reopen the compute architecture. The historical M1 price anchor remains visible; a later SKU/price change needs cost reconciliation only.

No new premium sensors. M1 electronics/assembly selections remain unchanged. Additional planning allocation remains **INR 247,150**. The remaining **INR 2,850 stays reserve**, not a shopping list. M1's price/contingency reserves are not reallocated to features.

## Read this package in order

| Document | Design coverage |
|---|---|
| [01_SYSTEM_ARCHITECTURE](01_SYSTEM_ARCHITECTURE.md) | Nodes, local/cooperative/monitoring paths, lifecycle, processing and maturity |
| [02_INTERFACE_CONTROL](02_INTERFACE_CONTROL.md) | Hardware interfaces, signal reservations, observations, time, existing Protocol V2 boundary |
| [03_POWER_AND_PROTECTION](03_POWER_AND_PROTECTION.md) | Energy domains, regulation, return paths, fuse/load sizing and independent interruption |
| [04_MECHANICAL_AND_CALIBRATION](04_MECHANICAL_AND_CALIBRATION.md) | Layout, coordinate frames, dimensional rules, wheel geometry and calibration |
| [05_ALGORITHMS_AND_OPERATING_ENVELOPE](05_ALGORITHMS_AND_OPERATING_ENVELOPE.md) | Perception, association, uncertainty, observability, TTC and proposed R2 decision logic |
| [06_NAVIGATION_AND_FLEET](06_NAVIGATION_AND_FLEET.md) | RTK/base, localization, mine graph, guidance and cooperative conflict intervals |
| [07_HMI_AND_CONTROL_ROOM](07_HMI_AND_CONTROL_ROOM.md) | Driver/supervisor/fleet displays, offline maps, events, replay and monitoring authority |
| [08_FAILURE_SECURITY_AND_RECOVERY](08_FAILURE_SECURITY_AND_RECOVERY.md) | Fault effects, resource limits, security and restart behavior |
| [09_VALIDATION_PLAN](09_VALIDATION_PLAN.md) | Requirement-linked tests, acceptance gates, experiments and evidence |
| [10_FEASIBILITY_VIABILITY_IMPACT](10_FEASIBILITY_VIABILITY_IMPACT.md) | Budget/workload feasibility, operation, impact metrics and industrial transition |
| [11_AUDIT_AND_RELEASE_GATES](11_AUDIT_AND_RELEASE_GATES.md) | Coverage audit, unresolved inputs, next work and release conditions |

## Source and authority order

1. This user's Master-2 handoff clarification, particularly the three boundaries above and reserve-only instruction.
2. The twelve unchanged M1 files in the parent directory: requirements, exact selections, BOM, interfaces, limitations and exclusions.
3. Current software identity/status and Protocol V2 for what exists today, not earlier conversational plans or superseded V1 material.
4. Manufacturer documentation for interface capability; measurements of the actual delivered assembly for physical performance/ratings.
5. Proposed M2 design targets, always labelled as targets rather than test results.

R1 source references inspected: [PROJECT_STATUS](../../PROJECT_STATUS.md), [release manifest](../../TARK_RELEASE_MANIFEST.md), [Protocol V2](../../ESP32_PROTOCOL_V2.md), [replay guide](../../REPLAY_GUIDE.md), and current runtime/pipeline/API source. Historical test counts were not rerun or upgraded to R2 evidence.

## Explicit maturity separation

| Layer | Status in this handoff |
|---|---|
| R1 existing software/portable protocol evidence | Preserved historical software-evidence baseline; not revalidated here |
| R2 component choices | Frozen by M1 plus regional-platform clarification above |
| R2 algorithms/navigation/fleet/HMI extensions | Designed here; implementation and tests remain future work |
| Electrical/mechanical detail | Parameterized design; exact values requiring measurements/ratings remain HOLD |
| New physical integration | Not performed; no COM/USB/I2C access, flashing or motor activity |
| Mining safety/industrial benefit | Unvalidated; no certification, guaranteed collision avoidance or production-gain claim |

Current deployed/local behavior is not changed by these documents: traction remains `DISABLED_PHASE_1`; permitted speed and both applied wheel outputs remain zero. NORMAL in the current software is not authorization to move. A future motion-capable model needs a separately approved phase-bound release.
