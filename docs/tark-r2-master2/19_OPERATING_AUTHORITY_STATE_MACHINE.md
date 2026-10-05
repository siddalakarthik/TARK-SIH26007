# 19 — Operating authority state machine

R2 DESIGN, not a modification of current R1 enums or policy. States remain exactly NORMAL, WARN, RESTRICT, STOP, UNKNOWN. Represent decision confidence/capability separately from applied-output authority.

## Deterministic evaluation order

Each 20 Hz proposed decision tick snapshots immutable current evidence/configuration; evaluates all constraints and stores every reason. Compute candidate state in this order:
1. STOP if stop_latched, local output inhibition/cutoff evidence requires it, a qualified immediate hazard satisfies the approved stop rule, or future enabled model loses its essential endpoint supervision.
2. UNKNOWN if a required evidence/coverage/motion/time/configuration dependency is invalid or unavailable.
3. RESTRICT if a qualified cap is below requested/current upper-bound speed, or a reviewed degraded-mode policy explicitly imposes a lower capability.
4. WARN if emerging qualified hazard or relevant advisory degradation requires attention.
5. NORMAL only if all task-required dependencies and envelope are usable and no higher rule applies.

Unknown physical-cutoff sensing is not false “active” or “released”; it blocks future motion rearm until the physical procedure/gate establishes the required condition. STOP does not prove wheels stopped.

| State | Entry / capabilities | Exit | Driver / log |
|---|---|---|---|
| STOP | Qualified stop rule or latched inhibition; no motion grant | Cause cleared, rearm for latched events, fresh required evidence, recovery dwell | STOP + action/reason; retain latch source |
| UNKNOWN | Cannot establish supported operation; zero authorized motion | Every missing dependency restored, gates passed and dwell | Evidence insufficient; list lost capabilities |
| RESTRICT | Known reduced envelope/capability | Cap above request plus hysteresis and restored evidence | Restricted capability and binding constraint |
| WARN | Relevant warning but qualified envelope retained | Warning below clear threshold for dwell | Attention + hazard/action, not “safe” |
| NORMAL | Qualified task envelope with no active higher condition | Immediately on new hazard/fault | Within characterized model; not guaranteed safety |

## Hysteresis and restoration

### Task dependency profiles

Select and record the profile before a test; never switch to a weaker profile automatically when a sensor fails. These are proposed R2 dependency rules, not changes to the R1 runtime.

| Profile | Required for a supported operating assessment | Optional support / failure treatment |
|---|---|---|
| LOCAL_FORWARD | Qualified radar geometry, motion, contiguous coverage for the tested target domain, clock/frame/calibration integrity, approved stopping parameters and state configuration | RGB/thermal semantics may be optional only if the actual coverage characterization does not depend on them; losing optional support yields WARN, losing required coverage yields UNKNOWN |
| MINE_GUIDANCE | LOCAL_FORWARD plus qualified localization, unambiguous usable map context, current approved graph/restrictions and route feasibility | Mere internet/basemap loss is not local route loss when approved local geometry is available; no confident maneuver from ambiguous pose |
| COOPERATIVE_CONSTRAINED_SECTION | MINE_GUIDANCE plus all expected participating peer states, bounded remote age/uncertainty and valid conflict-region geometry | A missing peer makes cooperative assessment UNKNOWN; retain prior qualified conflict rather than relax it |

All profiles require the endpoint supervision/identity/expiry conditions additionally before any future enabled motion phase; the present phase always has zero authority. Display-only diagnostic inspection can continue without a supported operating assessment, but it cannot label missing required evidence NORMAL. A known independent STOP cause takes priority over UNKNOWN. A reviewed policy may choose a more conservative restriction; it cannot omit a required dependency to manufacture a valid cap. Brownout, reset, stale-command and physical-release testing remain gates in 44.

Escalation is immediate; no minimum dwell delays STOP/UNKNOWN. Initial software-test restoration rule: at least 3 fresh valid observations per required source AND 1 s continuous good condition. If source rate makes this longer, wait longer. This is a proposed fixture target requiring validation, not an implemented R1 parameter. Hazard-clear thresholds must be more conservative than entry thresholds in the direction that avoids chatter. Their numeric TTC/distance values remain tied to validated motion models, not universal constants.

Fault onset intersects capability with the pre-fault capability set and may only preserve/reduce authorized output. State names are not a numeric safety ordering: UNKNOWN must not restore a cap removed in RESTRICT. Explicit recovery is required before a capability can return. Preserve last known hazard and add uncertainty rather than erasing it.

Reason priority: physical/local inhibit → immediate qualified hazard → time/config integrity → missing required evidence → margin/cap restriction → emerging hazard → optional-source degradation → normal evidence. Stable secondary sorting by reason code and source ID guarantees repeatability.

Taxonomy examples: SENSOR_RADAR_STALE, SENSOR_RGB_DEGRADED, SENSOR_THERMAL_UNAVAILABLE, MOTION_UNKNOWN, LOCATION_AMBIGUOUS, LOCATION_RTK_DEGRADED, FLEET_BLIND_CURVE_CONFLICT, FLEET_PEER_STALE, GEOMETRY_COVERAGE_UNKNOWN, ENVELOPE_MARGIN_INSUFFICIENT, ENDPOINT_COMMAND_EXPIRED, ENDPOINT_SESSION_LOST, RECORDING_UNAVAILABLE. PHYSICAL_CUTOFF_ACTIVE requires verified observation; otherwise status UNKNOWN. New taxonomy maps to a reviewed wire reason set later, not arbitrary V2 extensions.

Log previous/candidate/final state, full evidence IDs, capability mask, cap, reasons, dwell/latch transitions and displayed action. All present-phase command values remain zero / DISABLED_PHASE_1. Test every transition, simultaneous reasons, loss during recovery and unknown-to-normal prohibition.
