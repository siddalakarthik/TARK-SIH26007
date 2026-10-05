# 08 — Radar perception and persistent tracking

R2 DESIGN. IWR1843BOOST is the only primary radar. LD2450 stays a separate bench asset; neither parser nor bytes are interchangeable.

## Acquisition and processing choice

Select the EVM's documented processed UART/USB path, not raw ADC capture. Before implementation pin the exact TI firmware/demo, SDK, profile and packet specification by version/hash. One adapter owns configuration and data interfaces. Validate packet boundaries, declared lengths, message types, counts, finite values and source sequence/time before normalization; cap buffer and detection counts. Unsupported profile is UNAVAILABLE, not guessed decoding. See [TI EVM documentation](https://www.ti.com/tool/IWR1843BOOST).

Pipeline: processed points → validation/time → body transform → optional clustering → persistent tracks → relative-motion validity → corridor relevance → risk contribution. Preserve valid-empty reports and raw diagnostics distinctly from missing data.

## Selected methods

| Stage | Method / parameters | Reason, cost and failure |
|---|---|---|
| Clustering | DBSCAN on normalized x/y and Doppler consistency; epsilon scales with characterized angular/range error, min_samples versioned | Groups multiple returns per object, no assumed object count. Indexed typical O(n log n), worst O(n²). Density varies with range; retain useful singleton hypotheses rather than erase sparse targets |
| Tracking | Constant-velocity Kalman filter on [x,y,vx,vy] in locally stable frame, timestamp-driven F and Q | Small bounded state; requires ego-motion compensation or explicit relative-frame model. Turning/acceleration grows uncertainty |
| Measurement | Cartesian position update when documented; radial velocity updates via an EKF measurement only when native Doppler sign/frame is verified | Doppler alone cannot supply both vx/vy. Do not invent unobserved elevation or velocity |
| Association | Mahalanobis gating then Hungarian global assignment with unassigned cost | O(k³) for capped association matrix; avoids greedy identity swaps. Ambiguous costs remain ambiguous |
| Lifecycle | TENTATIVE, CONFIRMED, COASTING, LOST; hit/miss/time criteria configuration-controlled | Identity is a generated track ID plus source epoch, never a sensor slot |
| Relevance | Uncertain object footprint intersected with vehicle's qualified swept corridor | Off-axis returns are not automatically head-on hazards; unknown corridor stays unknown |

For prediction x'=F(dt)x, P'=F P Fᵀ+Q(dt). Innovation r=z−h(x), S=H P Hᵀ+R; gate by rᵀS⁻¹r. Calibrate R/Q and gate false-association tradeoffs; do not set covariance equal to range resolution or signal-strength percentage. Singular/non-positive covariance is an invalid update. Bound dt; never predict indefinitely after loss.

Initial software-test targets: cap 256 points/frame and 64 tracks, confirm 3 matched observations within 5 valid frames, coast at most the stream's 300 ms stale budget. These are proposed fixture parameters, not a qualified TI maximum or real safety deadline. Overflow produces explicit lost-coverage diagnostics.

Track contract: track_id, position_vehicle_frame, velocity_vehicle_frame with observability flags, range, radial_velocity, covariance, first_seen/last_update, age, source_support, class_if_available, relevance, association status, calibration/profile IDs. Covariance expands while coasting. Unmatched radar geometry survives without an RGB class.

## TTC and CPA

For positive range r and verified closing radial rate r_dot<0, radial TTC=r/(-r_dot). Label it a constant-rate radial approximation; only use as collision TTC when trajectory/corridor geometry supports that interpretation. NON_CLOSING has null seconds; missing evidence UNKNOWN; malformed/stale evidence INVALID. Never abs(velocity) or zero fallback.

With relative planar position p and velocity v in one frame/time, t_CPA=−(p·v)/(v·v). For a bounded horizon H use t*=clamp(t_CPA,0,H), d_CPA=norm(p+v t*). Negligible v gives no finite closing-time evidence. If unconstrained t_CPA<0, closest passage is behind the current time. Compare uncertain footprints, not point distances. Crossing risk needs observable lateral motion; radial velocity alone cannot support CPA.

Validate known stationary/approaching/receding/crossing/multi-target scenes; identity swaps, ground/metal clutter, no returns, occlusion, profile mismatch, bad counts and stale time. No-target never proves a clear road.
