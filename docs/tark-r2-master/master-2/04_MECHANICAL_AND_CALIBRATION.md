# Master-2 — mechanical design and calibration

## 1. Mechanical concept

Retain the acrylic four-wheel chassis and TT drivetrain as the low-energy assistance-chain model. Put energy storage and heavier electronics low and near the support polygon centre. Use a rigid, short sensor support for radar/RGB/thermal; mount the IMU rigidly with a known orientation away from strong magnetic/current sources. Put the GNSS antenna where it has a clear sky view and a measured lever arm. These are placement constraints, not guessed millimetre coordinates.

If the measured combined payload/centre of gravity exceeds the chassis limit, do not place it on the robot to satisfy a diagram. First use the same frozen stack on a stable stationary characterization fixture, keep the model-motion experiment separate and labelled, and return the mobile mounting detail for review. This is a test staging constraint, not a stealth premium-chassis purchase or claim of integrated mobile operation.

```text
TOP VIEW — logical zones, NOT TO SCALE
             forward
                ^
   +-----------------------------------+
   | rigid forward sensor bar          |  radar/RGB/thermal apertures clear
   |                                   |
   |   low electronics / IMU reference  |  cooling and service access
   |   low protected battery placement |  keep traction wiring segregated
   |                                   |
   +-----------------------------------+
      wheel L sensor    wheel R sensor   geometry-dependent positions
       accessible manual traction disconnect, outside rotating parts
```

No sheet thickness, mast height, hole pitch, bolt size, shaft diameter or magnet gap is a fabricated as-built value. Select fastener/load paths after the measurements below. No sensor PCB is a structural cross-member.

## 2. Required dimension set and parametric layout

| Symbol / record | Actual measurement required | Design use |
|---|---|---|
| L_c, W_c, usable deck polygon | Chassis length/width, holes, edge clearances, battery/motor intrusions | Mount envelope and fastener positions |
| L_w, W_track, D_L, D_R | Wheelbase, track, rolling diameter under load | Support polygon, wheel-response scaling, skid-steer uncertainty |
| H_clear | Ground clearance at payload | Cable/guard clearance; no hanging leads |
| m_i, r_i | Actual mass and centre position of every installed assembly | Total payload and centre of gravity |
| Wheel-hub envelope L/R | Shaft/hub diameter, axial/radial space, rotating sweep, accessible face and achievable magnet gap/alignment | Exact carrier/magnet/mount selection inside frozen technology |
| Sensor reference points | Mounting holes, optical/RF origin orientation and cable bend envelope | Extrinsic calibration and service repeatability |
| Electronics enclosure | Airflow, connector clearance, fastener access and separation | Cooling and inspection; not airtight plastic around hot boards |

Total mass `m_total = sum(m_i)`; centre of gravity `r_CG = sum(m_i * r_i) / m_total`. In a simplified level rigid-body model, static tipping about an edge is related to `theta_tip = atan(d_edge / h_CG)`, where d_edge is the horizontal CG distance to that support edge. Actual slope, acceleration, uneven ground, suspension/flex and cable forces reduce usable margin. These formulas guide review, not certify stability.

Mast bending stiffness and sensor alignment matter more than appearance. After mount/remount and at expected vibration, measure transform repeatability against the selected calibration tolerance. A taller mast increases moment and changes radar ground reflections; do not add height without a demonstrated benefit.

## 3. Two magnetic-angle wheel paths

Use one measured wheel/hub per side; retain the **14-bit SPI magnetic-angle technology**. The exact carrier and magnet geometry remain HOLD. Verify on-axis alignment and manufacturer gap/field requirements against the chosen assembly after measurement. Mechanically retain the magnet and protect rotating parts; adhesive alone is not assumed a qualified retention method.

The assembly must expose validity/error information, tolerate the actual runout and cable movement, and avoid boot-pin conflicts at the ESP32. Sample-target 100 Hz is not a sensor calibration. Raw angle quantization for a full-turn 14-bit code is `2*pi/16384` radians; accuracy can be much worse because of magnet/mount errors.

Signed displacement is derived only when unwrap is unambiguous: `delta_s = r_effective * delta_theta`. A gap that permits more than the allowed intersample rotation invalidates turn counting until re-established. A moving wheel on one side is not proof that both TT motors on that side work, and neither side measures true ground speed during slip.

Do not assume `yaw_rate = (v_R-v_L)/track` is accurate for a four-wheel skid-steer acrylic robot. It is only an initial kinematic relation; lateral scrub and effective track need empirical characterization. Do not convert it into an OEM dumper motion model.

## 4. Sensor-window and cable design

Keep radar antenna aperture and camera views unobstructed. A protective cover is not RF/LWIR-transparent merely because it is plastic or clear. Lepton must not be placed behind ordinary glass and then claimed to measure the outside scene. Any window/radome needs measured transmission/attenuation and recalibration in the assembled geometry.

Segregate motor leads from small-signal/IMU wiring, use strain relief, protect connectors against pull and leave service loops outside wheel sweep. Mount thermal/RGB/radar rigidly relative to one another. Keep the IMU away from ferrous mounts, magnets and high-current loops as far as actual geometry permits; verify interference rather than promising a universal separation distance.

The consumer display/AP/hub/development boards have no assumed rain/dust/IP rating. Initial experiments are controlled and protected; mining weather exposure is outside the release.

## 5. Calibration and coordinate plan

R2 body frame: x-forward, y-left, z-up. Define and store `T_body_sensor`, its convention, uncertainty, date, mounting revision and reference point. World/local-map frame is ENU about a documented origin; screen coordinates are separate. Validate legacy adapter axes before converting them. Store units explicitly.

| Calibration | Method / data | Acceptance evidence |
|---|---|---|
| RGB intrinsics | Known target geometry at several image positions/distances >= fixed-focus boundary; actual active resolution | Residuals on held-out images, distortion model and exposure/focus settings |
| Thermal intrinsics/extrinsics | Reference visible in both modalities with known safe geometry and thermal contrast | Association residuals by position/range; no absolute temperature claim without appropriate reference |
| Radar axes/range | Surveyed reflector locations and target motion in a controlled scene | Range/angular/radial-velocity errors, sign checks and profile ID |
| Cross-sensor extrinsics | Repeatable multimodal target at several positions, not one favourable example | Transform uncertainty; radar sparse points cannot guarantee pixel-level dense depth |
| IMU axes/bias | Static poses, controlled rotations and warm-up record | Axis signs, bias/drift and magnetic-disturbance flags; never calibrate near unknown motor fields and assume universal validity |
| Wheel scale | Actual rolling circumference under representative load and independent displacement reference | Left/right scale, slip/mismatch and unwrap-validity bounds |
| GNSS reference | Base coordinate method, antenna lever arms, known course marks and datum | Reference uncertainty and absolute-versus-relative claim scope |
| Time alignment | Log device and host timestamps; controlled common observable event where possible | Delay/jitter bounds per channel; no shared hardware trigger claimed |

Changing a mount, lens setting, radar profile or antenna reference invalidates affected calibration until checked. Version calibration records and replay the original IDs; never apply a new transform silently to historical evidence.
