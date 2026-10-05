# 13 — Localization engine

R2 design selects a planar error-aware EKF plus separate discrete road matching. Do not assume the BNO085's internal fusion is a navigation solution.

## State and updates

Initial state x=[east,north,yaw,speed,gyro_z_bias]. Predict yaw with gyro-minus-bias; propagate position with speed and yaw using measured dt. Add process noise for acceleration, slip and bias. Optional accelerometer propagation is withheld until gravity/bias compensation is validated; no fictitious inertial accuracy.

GNSS updates position and supported velocity; wheel speed updates only when slip/plausibility checks pass. Use measured/calibrated covariance, innovation gates and explicit rejected measurements. IMU orientation may supply a qualified yaw observation only with known reference/magnetic validity; do not double-count fused orientation and its correlated raw gyro as independent data. GNSS heading updates need adequate displacement/speed relative to uncertainty.

R_B/E lever-arm correction: body reference position = antenna position − rotated antenna-to-body offset. Preserve ENU datum/origin and altitude type; ellipsoidal height is not automatically road height. Transform uncertainty including lever arm/yaw/reference error.

Output LocalizationEstimate: position/altitude (nullable), yaw/reference, speed/source, covariance, quality, source support, current_edge nullable, along_track_distance, map revision, acquisition/evaluation time and expiry. Matching does not overwrite the unconstrained estimate or shrink covariance merely to put the marker on a road.

## GNSS quality and corrections

Normalize NO_FIX, SINGLE, DGPS, FLOAT, FIXED, STALE, INVALID only where actual receiver messages document those states; retain raw status and reject unmapped codes. FIXED is a receiver mode, not an integrity certificate. Check fix age, correction age, solution type, reference/base identity, reported accuracy if present, innovation and plausible motion. Never invent DOP-derived accuracy without a justified model.

Base GNSS → one laptop receiver owner → bounded authenticated correction distribution → Jetson/Pi receiver owner → respective rover. A moved base/wrong reference invalidates related position confidence even if both rovers agree. Averaged base coordinates can support limited relative experiments but not surveyed absolute accuracy.

## Loss and recovery

GNSS loss starts bounded dead-reckoning with covariance growth only within a characterized time/distance budget; until characterized, precise navigation is UNKNOWN immediately. Wheel slip removes wheel aiding. Magnetic disturbance removes magnetic yaw. Map ambiguity preserves multiple candidate edges. Do not report one certain turn while covariance overlaps roads.

Recovery requires new valid fixes, reference compatibility, plausible residuals and the recovery dwell in [19](19_OPERATING_AUTHORITY_STATE_MACHINE.md), not just RTK FIX text. Test wrong base, common-mode shift, stationary course noise, tunnels/occlusion, gyro bias, wheel slip, timestamp rollback and remount.

Source scope: [Quectel LG290P](https://www.quectel.com/product/gnss-lg290p/) and [M1](../tark-r2-master/06_SENSOR_PERFORMANCE_TARGETS.md). Exact firmware configuration commands remain implementation-detail verification, not invented here.
