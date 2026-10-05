# 06 — Sensor geometry and calibration

## Frames and field limits

B = forward/left/up; E = local east/north/up with explicit datum/origin. T_BS maps sensor S into B: p_B = R_BS p_S + t_BS. Optical/native radar conventions are explicitly transformed, never silently renamed. Propagate covariance with Jacobians plus calibration error.

| Sensor | Geometry / useful field | Calibration |
|---|---|---|
| IWR1843BOOST | Profile-dependent field/near zone; no guaranteed TARK range | Known reflectors at multiple ranges/angles, clutter and residuals |
| B0200 | 100° diagonal, not horizontal; focus about 1 m–infinity | Intrinsics/distortion across chart poses/depth; held-out reprojection |
| Lepton 3.5 | 160×120, 57° horizontal, 8.7 Hz; pixels-on-target limits | Visible/thermal fixture, FFC, bad pixels, mode and extrinsics |
| BNO085 | Orientation/rate, no distance field | Bias, known rotations, signs, body alignment, magnetic disturbance |
| GNSS | Antenna position, not body center | Lever arm, datum/base coordinates, reference uncertainty |
| Wheels | 14-bit resolution, not accuracy | Marked rotations, sign, eccentricity, gaps and measured wheel radius |

u = pi(K R_CB(p_B−t_BC)) only for positive optical depth and valid distortion model. Uncertain radar elevation produces a projected region, not an exact pixel. A ground-plane assumption needs a qualified surface. Co-mount closely; baseline parallax scales approximately d/Z. A homography is not universal across depths. Useful overlap is intersection of characterized fields including bracket/chassis occlusions.

## Record and method

Each calibration stores CALIBRATION_ID, date/clock, method, parameters/units, residuals/uncertainty, validity conditions, software/hardware versions, mount revision, operator/reviewer, original run IDs and reference uncertainty. Missing transform never defaults to identity in real mode.

1. Measure unpowered datum/mounts. Capture labels/photos.
2. Qualify acquisition, then RGB multi-pose intrinsic calibration with held-out checks.
3. Characterize thermal frames/FFC; use safe reference targets and independently qualify absolute-temperature mode.
4. Fit RGB/thermal and radar/camera extrinsics across depths with bounded alignment time. Preserve unmatched evidence.
5. Align IMU and validate rotation signs/bias; magnetometer near steel/motors is not trustworthy by default.
6. Measure antenna lever arm and relate base/course/map datum. Averaging coordinates is not a surveyed absolute reference.
7. Calibrate wheel sign, angle, diameter, straight-line travel and turning against independent references. Skid-steer effective track may differ from geometric spacing.
8. Remove/reinstall mounts and repeat. Invalidate old calibration if allocated error is exceeded.

Repeatability tolerance is chosen from the spatial/angular error budget BEFORE measurements are evaluated. No invented millimeter acceptance. Manufacturer maximum range is not TARK characterized range. Physical tests remain pending.
