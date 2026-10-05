# Master-2 — algorithms and proposed operating envelope

**R2 algorithm design, not current production behavior.** R1 remains unchanged, with zero speed supplied to its provisional stopping calculation and zero commands. The following must be implemented and validated in a later authorized software task before any operational claim.

## 1. Processing order and invariants

Acquire → schema/identity checks → timestamps/freshness → calibrated observations → detection/tracking → uncertainty/disagreement → corridor relevance → relative motion → TTC/conflict evidence → supported distance/stopping model → state/reason → bounded request → endpoint validation → feedback → event/replay.

Mandatory invariants:

- Missing or invalid inputs remain missing/invalid; no false zero, hidden simulation or artificial confidence.
- An empty detection set is not a visibility certificate. A detector's silence does not establish free space.
- More uncertainty cannot increase a calculated positive operating envelope when other inputs are held fixed.
- A fault cannot silently grant an authority that was previously constrained. Recovery needs new qualified evidence, not merely a restarted process.
- Semantic confidence, covariance, calibration uncertainty and hardware health are different quantities; none is a universal “AI safety score.”
- The present phase caps requested and applied outputs at zero, independently of illustrative R2 calculations.

## 2. Acquisition and evidence-quality engine

Every observation carries the interface envelope in document 02. Use separate validity tests for identity/profile, finite/bounded fields, complete packet, timing, calibration and operating-domain membership. Preserve rejection reasons and counters. Sensor quality is a vector of these facts rather than one arbitrary weighted percentage.

For each source distinguish UNAVAILABLE, invalid measurement, valid but aging, and usable within its characterized domain. Health ONLINE describes communication/acquisition, not guaranteed hazard visibility. A recognized receiver or matching USB ID is not physical calibration or proof the correct sensor is aimed at the road.

Store raw diagnostics with bounded retention, but make normalized observations the single decision-input boundary. A new TI adapter must use the selected firmware/profile's documented processed packet definition. Do not run LD2450 bytes through a TI parser or infer target identity from a packet slot number.

## 3. Radar geometry and tracking

Normalize documented radar measurements into range/bearing/radial velocity and/or Cartesian coordinates, with frame/profile identity. Do not fabricate full 2D target velocity from one radial component. If the selected demo exports tracks rather than detections, preserve that distinction and avoid presenting a second tracker as independent evidence.

Initial R2 tracking design: bounded multi-target constant-velocity Kalman tracks in the local frame, timestamp-based prediction, gated measurement updates and global nearest-neighbour assignment. Use measurement covariance established by characterization; do not convert signal amplitude or range resolution directly into a universal position covariance.

For measurement z and prediction h(x), innovation `r = z - h(x)` and innovation covariance `S = H P H^T + R`. Association uses `r^T S^-1 r` with an explicitly selected validation gate and physical plausibility checks. A candidate outside the gate remains unassociated; it is not forced into the nearest visible box. Ill-conditioned covariance or invalid dynamics produces an invalid update, not a silently confident track.

Track lifecycle: tentative → confirmed → coasting with growing uncertainty → expired. Confirmation/deletion limits are controlled parameters to select from data; coasting does not create fresh sensor evidence. Bound target count and expose truncation. Track identity changes, merges and splits must be logged; a slot ID is not a permanent obstacle ID.

## 4. RGB and thermal perception

RGB provides class hypotheses, image position, road-context cues and visibility degradation indicators. Use a compact detector evaluated on relevant scenes, with versioned model/weights/class list, license, input resolution and held-out dataset. No specific pretrained weight is claimed mine-ready; selecting and validating weights is a software/data work item, not a new hardware choice.

Thermal supplies thermal-contrast regions and, after independent validation, class hypotheses. Preserve raw/radiometric values when available alongside display data; palette colour is not temperature. FFC, frozen frames, bad pixels, low contrast and saturation can invalidate a frame. The 8.7 Hz channel must not acquire false independent evidence through interpolation.

Do not estimate metric range from a thermal/RGB box without a separately validated geometric method. Radar is the primary selected metric obstacle channel. A visible road edge is not a surveyed lane boundary, and a thermal silhouette is not necessarily a person.

## 5. Association and disagreement

Project a radar hypothesis into camera coordinates only through a qualified extrinsic/intrinsic model and bounded time alignment. Camera projection is `u ~ K * (R * p + t)` for points in front of the imager, with uncertainty propagated to an image region. Sparse radar returns need not lie at the centre of a visible object.

Retain hypotheses such as RADAR_ONLY, RGB_ONLY, THERMAL_ONLY, ASSOCIATED and DISAGREEMENT as evidence annotations, not new motion-authority states. A one-to-many overlap is ambiguous, not automatically a match. Account for parallax/occlusion and different sensor apertures.

Do not treat correlated RGB/thermal classifier errors or shared calibration errors as independent votes. If cross-correlation is unknown, preserve separate hypotheses or use a reviewed conservative fusion method; do not shrink covariance by naive averaging. Explicitly log why association was accepted/rejected.

## 6. Corridor relevance and motion

Use body-frame geometry and, only when localization/map quality permits, a road-aligned corridor. Expand the swept vehicle footprint by position, track, alignment, time and model uncertainty. On a curve, evaluate the swept path rather than an infinite straight rectangle.

A target is relevant if its uncertainty-supported occupancy can intersect the corridor over the prediction horizon. If road assignment or heading is ambiguous, preserve multiple plausible corridors or declare corridor capability unavailable; do not discard targets using an unreliable road label.

Wheel response is auxiliary motion evidence. GNSS, inertial and wheel estimates can disagree because of slip, timing, antenna lever arm, multipath or wheel-sensor faults. The current model must not silently substitute zero speed when velocity is missing and then advertise a short stopping requirement.

## 7. TTC and supported distance

For a justified common longitudinal path and positive closing speed, a simple TTC is `gap / closing_speed`. Both numerator and denominator need validity, geometry and uncertainty. For receding or near-zero closing motion display NOT APPLICABLE; for invalid geometry/age display INVALID/UNAVAILABLE, not infinity labelled safe. General crossing encounters use document 06's conflict intervals instead of this scalar.

Use a conservative lower gap bound and upper positive closing-speed bound when computing an earliest plausible conflict time. If those bounds cannot be established, report uncertainty rather than a precise number. Radar radial velocity alone is not a general crossing-target closing speed.

Define `D_supported` as the distance along the relevant corridor supported by a validated perception/coverage model under present conditions. The nearest target range and sensor maximum range are **not** that model. Radar-only valid-empty output cannot increase `D_supported` to a catalogue maximum. Before coverage characterization, the supported positive motion envelope remains unestablished.

## 8. Proposed stopping/envelope model

For an explicitly characterized operating case:

`D_required(v) = v * T_bound + v^2 / (2 * a_effective) + M`

T_bound includes bounded acquisition age, processing, communication, endpoint response and applicable operator/actuator response. It is not the Protocol V2 TTL. `a_effective > 0` is an independently justified conservative deceleration under the specified load/slope/adhesion conditions; M accounts for residual uncertainties. Unknown parameters prevent a positive validated speed claim.

For the simplified model with known nonnegative available distance `D_supported - M`, a candidate speed limit is:

`v_model = -a_effective*T_bound + sqrt((a_effective*T_bound)^2 + 2*a_effective*max(0, D_supported-M))`

The actual admissible bound would additionally be the minimum of validated platform, road, curvature, localization, sensor-domain and fault constraints. This inversion is a design equation, not implemented authority. **Current phase cap = 0**, so no positive model output may reach the motor command or be labelled an approved current permitted speed.

Robot coast/brake measurements apply only to that model configuration. They cannot determine HEMM stopping distance. Do not infer friction or dumper braking parameters from TT-motor results.

## 9. State and explanation design

Retain existing state vocabulary: NORMAL, WARN, RESTRICT, UNKNOWN, STOP. Fault is a diagnostic condition, not a casually added sixth wire state. R1's existing semantics are not changed; the following is proposed R2 policy to be reviewed and tested.

| State | Intended R2 meaning | Required explanation |
|---|---|---|
| NORMAL | Required evidence available within characterized conditions; no active stronger constraint | Domain, speed bound and limiting evidence; never a blanket SAFE label |
| WARN | Qualified risk/context requires driver attention before a restriction threshold | Hazard, action and evidence. WARN policy is not currently production-integrated |
| RESTRICT | Valid evidence supports a smaller operating envelope than requested/current context | Binding constraint and reduced bound |
| UNKNOWN | Required evidence/model cannot support a trustworthy conclusion | Missing/stale/ambiguous source, affected capability; no positive authorization |
| STOP | Recognized stop condition/physical interruption or unacceptable hazard under the reviewed policy | Specific stop reason, latch/reset conditions and evidence |

STOP conditions cannot be hidden by UNKNOWN; insufficient evidence cannot default to NORMAL. Apply immediate tightening for relevant faults, with conservative recovery hysteresis based on fresh qualified evidence. Reset/acknowledgment never clears a physical or unresolved evidence condition by itself. Log previous/new state, evidence IDs, constraints and authority before/after.

## 10. Implementation evidence required

Version algorithms, calibration, radar profile, models, route graph and configuration together. Test uncertainty monotonicity, sensor removal, disagreement, association errors, clock faults, multiple targets, curves and overload. Run changes first on immutable replay in shadow mode. No current command/firmware policy is modified by this design.
