# 12 — Vehicle motion evidence

VehicleMotionEvidence contains speed_mps or null, speed_source, left/right wheel responses, direction, yaw_rate_rad_s, acceleration_mps2, heading_rad with reference, acquisition time, covariance/bounds, validity and source support. Units, body frame and timestamp provenance follow [07](07_EVIDENCE_AND_DATA_CONTRACT.md).

## Magnetic wheel paths

Two 14-bit SPI absolute-angle channels: one measured wheel per side. Exact carrier/magnet/shaft assembly is PHYSICAL GEOMETRY DEPENDENT. No encoder supply, pin or rotor ratio is invented. For angle count c in [0,16383], theta=2πc/16384 after validated sign/zero configuration.

For valid successive samples, delta_theta=wrap_to_pi(theta_k−theta_prev), omega=delta_theta/dt, v_wheel=r_measured*omega. This requires maximum possible rotation between samples <π; otherwise turn count is ambiguous and response is INVALID. Reset, repeated timestamp, sample gap, error/parity flag or impossible rate invalidates the increment. Resolution 360/16384 degrees is not assembled angle accuracy. Actual carrier protocol/error checks must match its datasheet.

For qualified no-slip differential approximation: v=(v_L+v_R)/2, yaw_rate=(v_R−v_L)/b_effective under the x-forward/y-left convention. Sign tests are mandatory. Four-wheel skid-steer has scrub; effective b and slip invalidate simple kinematics. One sensor per side does not observe all four wheels independently.

## Source arbitration

GNSS Doppler/velocity when valid may support ground-motion estimate under its quality/time model; GNSS course is not standstill heading. Wheel speeds are WHEEL RESPONSE, never ground truth. IMU gyro aids short-term yaw; acceleration needs gravity/orientation validity. Do not double-integrate BNO085 acceleration into claimed long-term positioning.

Compare wheel/gyro/GNSS residuals against uncertainty and persistent mismatch windows. Wheelspin, sliding, uneven radius, turn differential and magnetic faults are distinct candidate causes, not automatically motor failure. If sources conflict, widen uncertainty or withdraw the estimate; averaging cannot manufacture certainty. Unknown current speed cannot become zero in a supported stopping calculation.

Command-response check stores requested/accepted/applied command, each wheel sample and elapsed time. No-motion expectation in R1 is ZERO OUTPUT; nonzero measured wheel response is observational (e.g., hand rotation), not proof software commanded it. Future delay/mismatch thresholds require actuator characterization. Current V2 has no wheel payload: see [20](20_LOCAL_ENDPOINT_ARCHITECTURE.md).

Validation: known rotations/marked distance, reverse, zero, wraps, missed samples, invalid flags, unequal wheels, lifted wheel/slip and external push. Independently measure reference distance/time and report uncertainty.
