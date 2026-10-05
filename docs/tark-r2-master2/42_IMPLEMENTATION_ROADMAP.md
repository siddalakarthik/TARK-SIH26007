# 42 — Controlled implementation roadmap

Revision M2-E1. Planning phases 0–17 below are work packages, not the current R1 Phase‑1 mode and not the industrial deployment phases. They authorize no purchase, wiring, flashing or motion. Fixtures and design work may proceed in parallel; physical work obeys [44](44_HARDWARE_COMMISSIONING_GATES.md). Dependency-based exits take precedence over calendar dates.

## Phase 0 — Freeze and baseline

- **Entry criteria:** Master‑1 and this controlled design available.
- **Work:** Record code revision, firmware/contract versions, selected hardware IDs and open holds; preserve R1.
- **Output:** Immutable implementation baseline and claim register.
- **Test:** Compare inventories and identify any contradictory legacy selection.
- **Exit criteria:** Every item has owner and authoritative reference; no silent replacement.
- **Dependencies:** No upstream implementation dependency.

## Phase 1 — Power and physical interfaces

- **Entry criteria:** Phase 0; exact supply/board evidence for any assembly to be energized.
- **Work:** Resolve protection, conversion, connectors, return paths, inrush and motor isolation using measured load/identity.
- **Output:** Reviewed harness/power release and updated ICD physical pins.
- **Test:** Unpowered inspection then current-limited device-level power checks under H0/H1.
- **Exit criteria:** Required H0/H1 evidence signed; unknown battery or pin is still isolated.
- **Dependencies:** 04, 03, 44; hardware measurements, not guesses.

## Phase 2 — Sensor bring-up

- **Entry criteria:** Released individual interfaces; outputs disabled.
- **Work:** Identify each device/firmware; acquire documented streams one owner per port; record unavailable states.
- **Output:** Version-pinned adapters and captured commissioning fixtures.
- **Test:** Disconnect/reconnect, malformed input and acquisition continuity.
- **Exit criteria:** Normalized evidence is traceable to actual device/configuration; failures visible.
- **Dependencies:** Phase 1 for hardware; mocks may start after Phase 0.

## Phase 3 — Observation contracts and health

- **Entry criteria:** Phase 0 contract baseline; fixture inputs available.
- **Work:** Implement timestamps/clock mapping, source modes, validity, age, uncertainty and bounded queues.
- **Output:** Observation/health/time services with versioned schemas.
- **Test:** Future, duplicate, stale, invalid and reset-epoch cases.
- **Exit criteria:** No invalid data silently becomes usable; source modes never mix.
- **Dependencies:** 07 and 24; can proceed alongside Phase 2.

## Phase 4 — Radar perception

- **Entry criteria:** Phase 3 plus exact TI image/profile/packet contract.
- **Work:** Validate normalized radar input, cluster, track, compute qualified geometry and relative motion.
- **Output:** Radar pipeline with retained unclassified/sparse evidence.
- **Test:** Recorded known targets, identity switches, no-target packets and ego-motion cases.
- **Exit criteria:** Coverage not inferred from silence; errors measured against selected reference.
- **Dependencies:** 08; Phase 2 radar acquisition required for physical results.

## Phase 5 — RGB and thermal

- **Entry criteria:** Phase 3; pinned camera/thermal modes and licenses.
- **Work:** Implement acquisition health, candidate inference, FFC handling and thermal region evidence.
- **Output:** Independent RGB/thermal outputs with timestamps and quality.
- **Test:** Frozen frames, exposure changes, FFC, contrast loss and held-out runs.
- **Exit criteria:** No invented range/temperature/visibility; deadlines measured on selected workload.
- **Dependencies:** 09, 10, 26; device results depend on Phase 2.

## Phase 6 — Tracking and fusion

- **Entry criteria:** Validated per-sensor outputs plus calibrated transforms.
- **Work:** Associate time-aligned evidence with geometric gates; retain disagreement and correlation limits.
- **Output:** Persistent track and association records.
- **Test:** Ambiguous crossing, unmatched returns, time skew and common calibration error.
- **Exit criteria:** No forced class/range association; covariance/support remain defensible.
- **Dependencies:** Phases 4/5 and calibration 06.

## Phase 7 — Localization

- **Entry criteria:** Phase 3; known datum/base and qualified IMU/wheel contracts.
- **Work:** Implement GNSS quality, planar estimator, lever arms and uncertainty-aware map candidates.
- **Output:** Localization estimates and ambiguity records.
- **Test:** FIXED/FLOAT transitions, outages, wheel slip, yaw bias and datum mismatch.
- **Exit criteria:** Uncertainty grows on lost support; no false precision from map snapping.
- **Dependencies:** 12/13; physical wheel carrier and endpoint payload can remain gated.

## Phase 8 — Mine map and navigation

- **Entry criteria:** Versioned graph plus Phase 7 estimates or labelled fixtures.
- **Work:** Validate road permissions/closures and implement route/maneuver pipeline.
- **Output:** Dijkstra route, candidate edge, maneuver and uncertainty outputs.
- **Test:** Disconnected graph, closure, wrong-way edge and overlapping road hypotheses.
- **Exit criteria:** Ambiguous location suppresses confident turn instructions; route never grants authority.
- **Dependencies:** 14/15; map validation and Phase 7.

## Phase 9 — Fleet and second node

- **Entry criteria:** Observation/identity contracts and authenticated local transport design.
- **Work:** Implement one GNSS owner per node, base correction distribution and bounded telemetry relay.
- **Output:** Age-aware A/B/base status and cooperative message capture.
- **Test:** Lost Wi-Fi, duplicates, clock drift, delayed frames and common correction loss.
- **Exit criteria:** Missing peers stay visibly stale; independent local sensing continues.
- **Dependencies:** 16/35; hardware network qualification separate.

## Phase 10 — Blind-curve prediction

- **Entry criteria:** Phases 7–9; validated conflict geometry.
- **Work:** Compute plausible route occupancy intervals, footprint and uncertainty.
- **Output:** UNKNOWN/POTENTIAL/HIGH/NO_CONFLICT evidence with reasons.
- **Test:** Opposing, crossing, merging, stationary and missing-peer scenarios.
- **Exit criteria:** NO_CONFLICT is scoped to supported hypotheses; never a clearance command.
- **Dependencies:** 17; no dependence on browser availability.

## Phase 11 — Safe operating envelope

- **Entry criteria:** Qualified motion/risk contracts; measured parameters for any physical claim.
- **Work:** Implement stopping inequality, usable coverage gates, constraint intersection and state policy in the controlled R2 path.
- **Output:** Shadow supported envelope and reasons; current output cap zero.
- **Test:** Boundary inversion, invalid inputs, stale coverage and fault monotonicity.
- **Exit criteria:** All positive shadow bounds justified; current Phase‑1 zero invariant holds.
- **Dependencies:** 18/19; operational deceleration and coverage remain physical evidence gates.

## Phase 12 — Driver HMI

- **Entry criteria:** Stable server-side observation and decision contracts.
- **Work:** Render glanceable state, reasons, speed/quality, hazards, navigation and mode.
- **Output:** Responsive monitoring-only driver view and accessible alerts.
- **Test:** Empty/stale/disconnected data, unknown TTC and simultaneous warnings.
- **Exit criteria:** No fake live status; no browser control authority; critical message readable.
- **Dependencies:** 21; Phases 8/11; fixtures allowed with persistent labels.

## Phase 13 — Control-room platform

- **Entry criteria:** Fleet/event API and role/security design.
- **Work:** Extend current app with fleet/detail/perception/incidents/replay/navigation/analytics/maintenance/admin views.
- **Output:** Role-gated control-room monitoring and audited context changes.
- **Test:** Unauthorized actions, server disconnect, stale peers, corrupt replay and missing media.
- **Exit criteria:** No direct drive; approved context writes are versioned/audited and cannot raise local authority.
- **Dependencies:** 22/23/35; no second application or duplicate protocol.

## Phase 14 — Physical R2 endpoint integration

- **Entry criteria:** H0–H5 plus exact board/sketch and reviewed physical binding; current Phase‑1 remains unchanged.
- **Work:** Bind tested codec/supervisor to verified transport, boot identity, tick and watchdog; implement reviewed wheel payload version.
- **Output:** Physical endpoint report and interoperable response/feedback evidence.
- **Test:** Reset, wrong session, stale/delayed command, link loss, clock and scheduler failure.
- **Exit criteria:** Zero-output build passes first; nonzero-output phase requires separate explicit release after age/enable/cutoff qualification.
- **Dependencies:** 20/43/44; no current authorization to flash or move.

## Phase 15 — Failure campaign

- **Entry criteria:** Integrated software and labelled fixtures; hardware faults only within released test gates.
- **Work:** Run all 28 fault cases and record timing, state, retained capabilities and recovery.
- **Output:** Traceable fault matrix and unresolved-defect list.
- **Test:** Repeat each case including recovery and compound failures.
- **Exit criteria:** Every required case has evidence; no fault increases authority.
- **Dependencies:** 27; prior subsystem tests and bounded queues.

## Phase 16 — Low-visibility validation

- **Entry criteria:** Approved safe experiment, references and stationary integrated system.
- **Work:** Collect clear-air, controlled artificial-aerosol, degraded and recovery runs.
- **Output:** Run-split dataset and measured KPIs with uncertainty.
- **Test:** Repeated targets/ranges with settings held and independent references.
- **Exit criteria:** Report both failures and successes; no mine-fog equivalence or fabricated result.
- **Dependencies:** 28/29; safety review, Phase 15 and physical acquisition gates.

## Phase 17 — Demo evidence

- **Entry criteria:** Only completed, verified prerequisites may be demonstrated.
- **Work:** Prepare primary 180-second story, extended inspection, manifest and honest fallbacks.
- **Output:** Demonstration package linking each claim to a run or design record.
- **Test:** Dry run including network failure and replay with mode labels.
- **Exit criteria:** Every visible claim has evidence; unfinished physical capabilities remain labelled design/simulation.
- **Dependencies:** 39/40/41; no arbitrary deadline overrides any test gate.

## Release ownership

A named electrical reviewer releases power/pins; a mechanical reviewer releases payload/mounting; software owners release schemas and regressions; the test lead releases experiment readiness and evidence. The project owner authorizes scope/phase transitions. No reviewer signature is implied by this document. An unresolved item blocks only its named release, not unrelated fixture development.
