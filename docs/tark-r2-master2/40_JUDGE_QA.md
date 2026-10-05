# 40 — Judge question bank

Revision M2-E1 • 2 October 2026. These are design answers, not claims that R2 hardware or software has already been validated. References identify the detailed engineering argument; they are not substitutes for measured test records.

## Q01 — Why is TARK more than a fog camera?

**Concise answer:** It combines qualified sensing, route context and explainable driver assistance.

**Deep technical answer:** An image does not establish obstacle range, stopping margin or route occupancy. TARK keeps each observation's age, uncertainty and support, then publishes the reason and limits of its recommendation.

**Evidence / file reference:** [Engineering detail](01_COMPLETE_SYSTEM_ARCHITECTURE.md).

## Q02 — Why keep the frozen sensor set?

**Concise answer:** The design must prove integration rather than accumulate sensors.

**Deep technical answer:** Master‑1 sets the technical baseline. A substitution requires evidence of incompatibility and a reviewed cost/interface impact; unused money is reserve, not permission to buy another premium sensor.

**Evidence / file reference:** [Engineering detail](../tark-r2-master/12_MASTER_FREEZE_CHECKPOINT.md).

## Q03 — Is the Jetson regional SKU a different architecture?

**Concise answer:** No; regional purchasing verification remains open.

**Deep technical answer:** The engineering platform is Orin Nano Super 8 GB developer kit. The 0000/0007 region issue requires supplier and warranty confirmation without changing host interfaces or inventing regional compliance.

**Evidence / file reference:** [Engineering detail](45_OPEN_ISSUES_REGISTER.md).

## Q04 — Can you release the motor GPIO wiring today?

**Concise answer:** No; GPIO16/17 are not frozen.

**Deep technical answer:** GPIO4/5 are preserved as reported left-channel connections, not proof of the complete board. Right-channel logical nets remain unassigned until exact PCB, memory, boot and interface conflicts are checked.

**Evidence / file reference:** [Engineering detail](03_ESP32_GPIO_RESERVATION.md).

## Q05 — Why not specify the wheel magnet carrier now?

**Concise answer:** Hub geometry is missing.

**Deep technical answer:** Two 14-bit SPI paths are frozen, but shaft alignment, air gap, magnet orientation and fixture retention require measurements and the selected sensor's documented limits. A plausible drawing is not a qualified assembly.

**Evidence / file reference:** [Engineering detail](05_MECHANICAL_LAYOUT.md).

## Q06 — What radar data reaches the Jetson?

**Concise answer:** Processed measurements from the selected TI firmware/profile.

**Deep technical answer:** The firmware image, serial configuration and packet definition must be pinned together. The software validates lengths and fields before normalized detections; USB acquisition does not imply access to raw ADC data.

**Evidence / file reference:** [Engineering detail](08_RADAR_PERCEPTION.md).

## Q07 — Does a radar no-target packet mean the road is clear?

**Concise answer:** No.

**Deep technical answer:** A valid empty packet proves acquisition, not detectability of every target. Usable coverage needs characterized target, angle, range and environmental conditions; unsupported space remains unknown.

**Evidence / file reference:** [Engineering detail](18_STOPPING_AND_SAFE_OPERATING_ENVELOPE.md).

## Q08 — Why cluster radar detections?

**Concise answer:** To form candidate objects without treating every return as an object.

**Deep technical answer:** Range-aware DBSCAN handles irregular clusters but can merge close targets or reject sparse returns. Retain relevant singletons with lower support and evaluate clustering against annotated physical target runs.

**Evidence / file reference:** [Engineering detail](08_RADAR_PERCEPTION.md).

## Q09 — Are the radar's target slots persistent object IDs?

**Concise answer:** No.

**Deep technical answer:** Slots can be reassigned. The proposed tracker uses prediction, Mahalanobis gating and assignment with explicit birth, confirmation, coast and deletion policies; identity switches remain a measured KPI.

**Evidence / file reference:** [Engineering detail](08_RADAR_PERCEPTION.md).

## Q10 — Does radar radial velocity equal vehicle-relative planar velocity?

**Concise answer:** No.

**Deep technical answer:** Radial velocity observes only the line-of-sight component. Planar motion requires multi-frame geometry, ego-motion treatment and covariance; unobservable tangential motion cannot be silently set to a confident zero.

**Evidence / file reference:** [Engineering detail](08_RADAR_PERCEPTION.md).

## Q11 — Which RGB model will run?

**Concise answer:** YOLO11n is a benchmark candidate, not a measured deployment result.

**Deep technical answer:** Compare the stated small-model candidates using the same held-out runs, input resolution and Jetson workload. Pin weights, preprocessing and license before adoption; nominal GPU throughput is not inference latency.

**Evidence / file reference:** [Engineering detail](09_RGB_PERCEPTION.md).

## Q12 — Is the camera field of view 100 degrees horizontally?

**Concise answer:** No; the frozen figure is diagonal.

**Deep technical answer:** Measure intrinsics and useful horizontal coverage at the actual capture mode. Near focus, distortion and cropping affect radar association, so datasheet diagonal FOV is not the usable safety corridor.

**Evidence / file reference:** [Engineering detail](06_SENSOR_GEOMETRY_AND_CALIBRATION.md).

## Q13 — Can low RGB contrast estimate visibility in metres?

**Concise answer:** Not without a calibrated physical reference.

**Deep technical answer:** Contrast, clipping and sharpness can flag image degradation. They also vary with lighting, exposure and scene texture; an uncalibrated score must not become a fog-distance input to the stopping envelope.

**Evidence / file reference:** [Engineering detail](09_RGB_PERCEPTION.md).

## Q14 — Can thermal imagery measure obstacle range?

**Concise answer:** Not in this design.

**Deep technical answer:** Lepton supplies thermal spatial contrast; it is not a range sensor. A range may be attached only through a valid, time-aligned association with independent geometry and explicit uncertainty.

**Evidence / file reference:** [Engineering detail](10_THERMAL_PERCEPTION.md).

## Q15 — Is every coloured thermal pixel a measured temperature?

**Concise answer:** No.

**Deep technical answer:** Pseudo-colour is a visualization. Radiometric interpretation requires the exact acquisition mode, metadata and calibration conditions; FFC/shutter periods and AGC imagery must not be interpreted as continuous calibrated temperature.

**Evidence / file reference:** [Engineering detail](10_THERMAL_PERCEPTION.md).

## Q16 — Can thermal sensing always see through fog?

**Concise answer:** No guarantee is made.

**Deep technical answer:** Target contrast, aerosol, path length, optics and environmental conditions affect evidence. The controlled experiment records when the thermal channel helps or fails rather than extrapolating a mine-wide penetration distance.

**Evidence / file reference:** [Engineering detail](28_LOW_VISIBILITY_VALIDATION.md).

## Q17 — Why three GNSS kits?

**Concise answer:** Two rovers plus one local base.

**Deep technical answer:** Rover A supplies main-vehicle context, rover B supplies cooperative-node context, and the base supplies corrections through the controlled network path. Each receiver has one I/O owner and its own identity and quality record.

**Evidence / file reference:** [Engineering detail](16_FLEET_TELEMETRY_AND_V2X.md).

## Q18 — Does RTK FIXED guarantee the position is correct?

**Concise answer:** No.

**Deep technical answer:** FIXED is a receiver solution status, not an independent ground-truth certificate. Antenna reference, base coordinates, multipath, correction age and datum must be checked against an independent reference.

**Evidence / file reference:** [Engineering detail](13_LOCALIZATION_ENGINE.md).

## Q19 — What changes when RTK becomes FLOAT?

**Concise answer:** Uncertainty and available navigation capability must change.

**Deep technical answer:** Do not hide the quality transition behind a smooth marker. Re-evaluate candidate road edges and conflict intervals; withhold confident turn instructions when the uncertainty overlaps multiple routes.

**Evidence / file reference:** [Engineering detail](13_LOCALIZATION_ENGINE.md).

## Q20 — What if both rovers lose corrections?

**Concise answer:** Treat the common failure explicitly.

**Deep technical answer:** Two degraded estimates are not independent corroboration. Keep solution quality visible, widen route occupancy bounds and report conflict uncertainty rather than cancelling warnings because both nodes lost precision.

**Evidence / file reference:** [Engineering detail](17_BLIND_CURVE_AND_JUNCTION_CONFLICT.md).

## Q21 — Does BNO085 provide long-term GNSS-free navigation?

**Concise answer:** No.

**Deep technical answer:** Gyro bias and integration drift grow without adequate external constraints. The planar estimator uses qualified GNSS and wheel aiding, and reports uncertainty growth; magnetic yaw is not automatically trusted near motors or steel.

**Evidence / file reference:** [Engineering detail](13_LOCALIZATION_ENGINE.md).

## Q22 — What is a 14-bit wheel angle worth?

**Concise answer:** One ideal code step is 360/16384 degrees, not that accuracy.

**Deep technical answer:** Noise, mounting eccentricity, sample timing and magnetic conditions dominate practical performance. The signed unwrap also needs less than half a revolution between valid samples or ambiguity must be reported.

**Evidence / file reference:** [Engineering detail](12_VEHICLE_MOTION_MODEL.md).

## Q23 — Can wheel speed be called true vehicle speed?

**Concise answer:** No; it is wheel response.

**Deep technical answer:** Slip, spin and differential turning break a direct ground-speed interpretation. Compare qualified wheel motion with GNSS/IMU evidence and retain mismatch; do not average away the inconsistency.

**Evidence / file reference:** [Engineering detail](12_VEHICLE_MOTION_MODEL.md).

## Q24 — Why not combine all sensor confidences into one number?

**Concise answer:** That can hide disagreement and correlation.

**Deep technical answer:** A detector score is not automatically a calibrated probability, and shared timing or geometry errors are correlated. Preserve source support and unmatched evidence; fuse only with defensible measurement models.

**Evidence / file reference:** [Engineering detail](11_MULTISENSOR_FUSION.md).

## Q25 — Radar sees an obstacle but RGB sees nothing: what happens?

**Concise answer:** The valid radar hazard remains.

**Deep technical answer:** RGB absence does not veto geometric evidence. The HMI can show an unclassified obstacle with qualified range while explicitly stating weak or absent semantic support.

**Evidence / file reference:** [Engineering detail](11_MULTISENSOR_FUSION.md).

## Q26 — RGB sees a truck but radar has no matching range: what happens?

**Concise answer:** Retain semantic evidence without inventing range.

**Deep technical answer:** The object may trigger an attention message under the stated policy, but it cannot acquire fabricated distance or TTC. Association must pass timing and geometry gates before numeric risk calculations use it.

**Evidence / file reference:** [Engineering detail](11_MULTISENSOR_FUSION.md).

## Q27 — Why use Dijkstra for mine routing?

**Concise answer:** It supports explicit nonnegative mine-edge costs without a heuristic assumption.

**Deep technical answer:** Filter closed and disallowed edges first. A* is a later option only with a proven admissible heuristic; route planning cannot grant local motion authority or override evidence limits.

**Evidence / file reference:** [Engineering detail](15_DRIVER_NAVIGATION.md).

## Q28 — What if localization matches two roads?

**Concise answer:** Show position uncertainty and suppress confident maneuvers.

**Deep technical answer:** Keep multiple candidate edges rather than snapping to the desired route. Conflict prediction must consider plausible occupancy on either edge until evidence disambiguates the position.

**Evidence / file reference:** [Engineering detail](14_MINE_NAVIGATION_GRAPH.md).

## Q29 — How does blind-curve prediction work without visual contact?

**Concise answer:** It compares route occupancy intervals from cooperative evidence.

**Deep technical answer:** Use route geometry, footprint, speed and position uncertainty, timestamp age and possible paths. Overlap produces a conflict assessment; it is not a right-of-way reservation or an autonomous clearance command.

**Evidence / file reference:** [Engineering detail](17_BLIND_CURVE_AND_JUNCTION_CONFLICT.md).

## Q30 — What about a stopped vehicle in a narrow section?

**Concise answer:** Its occupancy does not expire just because speed is zero.

**Deep technical answer:** A lower speed bound of zero can make the exit time unbounded. Keep the constrained section occupied or uncertain until fresh evidence supports clearance.

**Evidence / file reference:** [Engineering detail](17_BLIND_CURVE_AND_JUNCTION_CONFLICT.md).

## Q31 — What if the second node stops transmitting?

**Concise answer:** Keep a visibly stale node and uncertain occupancy.

**Deep technical answer:** Missing telemetry is not an empty road. Age out numerical predictions, retain the last known location with age, and remove cooperative confidence without erasing the operational warning silently.

**Evidence / file reference:** [Engineering detail](16_FLEET_TELEMETRY_AND_V2X.md).

## Q32 — Is this standardized direct radio V2V?

**Concise answer:** No; the prototype uses local-network cooperative telemetry.

**Deep technical answer:** Authenticated node messages are relayed through the control-room service over the local AP. Industrial V2X/private-network mapping is future deployment architecture, not a capability of the consumer AP.

**Evidence / file reference:** [Engineering detail](16_FLEET_TELEMETRY_AND_V2X.md).

## Q33 — When is TTC valid?

**Concise answer:** Only for qualified closing relative motion and applicable geometry.

**Deep technical answer:** Use r/(-r_dot) with negative range rate, valid timestamps and uncertainty bounds. Receding, invalid or unknown evidence uses explicit states rather than absolute speed, zero or a reassuring large number.

**Evidence / file reference:** [Engineering detail](08_RADAR_PERCEPTION.md).

## Q34 — How is a crossing hazard different?

**Concise answer:** Use closest point of approach and footprint overlap.

**Deep technical answer:** Time to CPA derives from relative position and velocity, then clips to the valid prediction horizon. Include uncertainty and vehicle extents; a positive straight-line TTC alone cannot characterize an intersection conflict.

**Evidence / file reference:** [Engineering detail](17_BLIND_CURVE_AND_JUNCTION_CONFLICT.md).

## Q35 — How is supported speed derived?

**Concise answer:** Invert the stopping inequality only when its inputs are qualified.

**Deep technical answer:** For D=D_usable-M, positive a and nonnegative delay, v_max=sqrt((a tau)^2+2aD)-a tau. Unknown coverage, motion or deceleration cannot yield a positive supported speed; current Phase‑1 output remains zero.

**Evidence / file reference:** [Engineering detail](18_STOPPING_AND_SAFE_OPERATING_ENVELOPE.md).

## Q36 — Where do the braking parameters come from?

**Concise answer:** From a controlled measurement/approval process, not copied HEMM values.

**Deep technical answer:** Robot coast, surface, payload and drivetrain differ from dumper braking. Industrial effective deceleration requires OEM/site-specific validation across relevant load, grade and environmental conditions.

**Evidence / file reference:** [Engineering detail](18_STOPPING_AND_SAFE_OPERATING_ENVELOPE.md).

## Q37 — Can a fault improve the operating state?

**Concise answer:** It must not increase available capability.

**Deep technical answer:** Evaluate capabilities and permitted bounds, not merely a colour ordering of five state names. Escalate immediately, and require sustained restored evidence plus explicit rearm for latched restrictions.

**Evidence / file reference:** [Engineering detail](19_OPERATING_AUTHORITY_STATE_MACHINE.md).

## Q38 — What stops a stale command?

**Concise answer:** Receiver-local expiry is part of the existing V2 supervision contract.

**Deep technical answer:** V2 binds sequence to a session and uses bounded lifetime after receipt. That is not an end-to-end age guarantee: delayed delivery needs a reviewed age bound before future positive-output operation.

**Evidence / file reference:** [Engineering detail](20_LOCAL_ENDPOINT_ARCHITECTURE.md).

## Q39 — Does ACK prove the robot moved or stopped?

**Concise answer:** No; ACK reports protocol acceptance.

**Deep technical answer:** Physical response requires independent feedback and timestamps. The current STATUS schema does not contain the proposed wheel-angle payload; extending it requires a controlled versioned contract, not a hidden field.

**Evidence / file reference:** [Engineering detail](20_LOCAL_ENDPOINT_ARCHITECTURE.md).

## Q40 — Is the current ASCII robot already Protocol V2?

**Concise answer:** No such equivalence is claimed.

**Deep technical answer:** The deployed sketch and exact board binding still need identification. Reuse the tested portable codec and supervisor, then qualify actual boot identity, scheduling, transport and watchdog behavior without weakening Phase‑1 gates.

**Evidence / file reference:** [Engineering detail](43_SOFTWARE_IMPLEMENTATION_PLAN.md).

## Q41 — Can the browser drive the robot?

**Concise answer:** No.

**Deep technical answer:** Driver and control-room pages inspect evidence and approved operational context. Motion requests remain local and bounded; browser loss, role changes or route edits cannot bypass the endpoint or physical cutoff.

**Evidence / file reference:** [Engineering detail](22_TARK_COMMAND_PLATFORM.md).

## Q42 — Why separate traction and compute supplies?

**Concise answer:** Motor transients and load faults must not be casually coupled into sensing power.

**Deep technical answer:** Use reviewed branch protection, return routing and qualified conversion. Single-ended control still needs an appropriate reference, but that does not justify sending motor return current through a sensor ground path.

**Evidence / file reference:** [Engineering detail](04_POWER_ARCHITECTURE.md).

## Q43 — Why not power the ESP32 from the L298N 5 V terminal?

**Concise answer:** That use is explicitly prohibited.

**Deep technical answer:** The module's regulator behavior and motor-domain disturbances do not qualify it as the logic supply. Separate qualified logic power and review USB backfeed; the damaged LM2596 is permanently excluded.

**Evidence / file reference:** [Engineering detail](04_POWER_ARCHITECTURE.md).

## Q44 — Is the traction cutoff a certified E-stop?

**Concise answer:** No; it is an independent prototype energy interruption function.

**Deep technical answer:** A rated latching manual DC disconnect must interrupt the sole traction feed independently of software. Contact rating, protection, reset behavior and stopping consequences still require qualification; power removal is not a guaranteed brake.

**Evidence / file reference:** [Engineering detail](44_HARDWARE_COMMISSIONING_GATES.md).

## Q45 — What happens when Jetson crashes?

**Concise answer:** The endpoint must expire commands independently, and manual cutoff remains available.

**Deep technical answer:** Current outputs are permanently zero. Future physical operation needs board-specific supervision and failure evidence; a desktop host test cannot prove physical watchdog scheduling or motor energy interruption.

**Evidence / file reference:** [Engineering detail](20_LOCAL_ENDPOINT_ARCHITECTURE.md).

## Q46 — What if recording storage fills?

**Concise answer:** Make evidence loss visible and prevent backpressure from blocking decisions.

**Deep technical answer:** Use bounded queues, event priorities, retention and explicit drop counters. A recorder failure cannot fabricate a complete incident or stall the local expiry path.

**Evidence / file reference:** [Engineering detail](23_INCIDENT_RECORDING_AND_REPLAY.md).

## Q47 — Is replay just playing a video?

**Concise answer:** No; it includes decision evidence and stateful reconstruction.

**Deep technical answer:** Record normalized inputs, configuration, calibration, clock mapping and state checkpoints. Compare original decisions with recomputation; GPU inference reruns are separately labelled experiments and are not promised bitwise identical.

**Evidence / file reference:** [Engineering detail](23_INCIDENT_RECORDING_AND_REPLAY.md).

## Q48 — How do you validate low-visibility behavior?

**Concise answer:** Use controlled artificial-aerosol experiments with clear-air and recovery baselines.

**Deep technical answer:** Record target geometry, reference method, sensor settings and exposure conditions by run. Safe experimental practice and independent reference are prerequisites; this is not recreation or certification of Bailadila fog.

**Evidence / file reference:** [Engineering detail](28_LOW_VISIBILITY_VALIDATION.md).

## Q49 — Can public datasets prove mine performance?

**Concise answer:** No.

**Deep technical answer:** Their optics, radars, labels and environments differ from TARK. They support pretraining or benchmark research; split custom TARK evaluation by independent run and reserve site claims for actual site evidence.

**Evidence / file reference:** [Engineering detail](26_DATASET_STRATEGY.md).

## Q50 — What exactly is novel?

**Concise answer:** The proposed integration emphasizes evidence limits, route-aware conflicts and replayable reasons.

**Deep technical answer:** The competitor matrix supports comparisons only where evidence exists. The package does not claim first-ever sensing, exclusive algorithms or superiority over unreviewed competitor implementations.

**Evidence / file reference:** [Engineering detail](30_NOVELTY_AND_DIFFERENTIATION.md).

## Q51 — Does the prototype cost represent price per dumper?

**Concise answer:** No.

**Deep technical answer:** The Master‑1 plan totals INR 247,150 with INR 2,850 unallocated reserve. Ruggedization, installation, maintenance, site mapping, connectivity and approval costs make industrial total cost a separate exercise.

**Evidence / file reference:** [Engineering detail](32_VIABILITY_AND_SCALABILITY.md).

## Q52 — Can you claim fewer accidents or a productivity percentage today?

**Concise answer:** No measured industrial benefit is claimed.

**Deep technical answer:** Tie warning lead time, false alerts, downtime and cycle-time evidence to matched trials. A student robot proves bounded integration behavior, not mine-wide collision prevention or guaranteed production gains.

**Evidence / file reference:** [Engineering detail](33_IMPACT_AND_BENEFITS.md).

## Q53 — What does blueprint PASS actually mean?

**Concise answer:** A coherent design is ready for controlled implementation.

**Deep technical answer:** It does not mean purchased, wired, implemented, physically verified or mine-certified. Exact unresolved facts and the particular releases they block remain visible in the open-issues register.

**Evidence / file reference:** [Engineering detail](46_ADVERSARIAL_REVIEW.md).

## Q54 — Can the whole design run offline?

**Concise answer:** Local sensing and bounded decisions must not require internet.

**Deep technical answer:** Local map assets, local identity/configuration validation and the local AP support the intended deployment. Cloud basemap or routing outages cannot grant authority or disable the sensor loop; regional network coverage remains unmeasured.

**Evidence / file reference:** [Engineering detail](24_SOFTWARE_ARCHITECTURE.md).

## Q55 — What prevents a replay packet from becoming live authority?

**Concise answer:** Mode, session, source identity and pipeline separation.

**Deep technical answer:** Replay runs in a non-actuating context with original provenance retained. Authentication and age checks reject unauthorized fleet/configuration inputs; CRC alone protects transmission integrity, not sender authenticity.

**Evidence / file reference:** [Engineering detail](35_SECURITY_ARCHITECTURE.md).
