# 04 — Power architecture and independent cutoff

DESIGN ONLY. Unknown ratings remain HOLD. No energization instruction.

## Selected domains

T traction: existing pack role retained, chemistry/current/protection/charger unverified. C compute: separate protected LiFePO4 electronics-battery category with matched charger, regulated 19 V. S sensors: regulated branches/USB and host logic. H network/HMI: protected AP/hub/display power. B bench: manufacturer-qualified supplies and owned laptop; reported SLA remains inventory only.

Select regulated DC conversion, not Jetson USB-C PD input. Exact electronics pack series/capacity depends on loads, converter input range, runtime requirement and payload. Separate domains do not imply galvanic isolation. Never infer chemistry from 7.78 V.

## Published supply versus demand

NOT PUBLISHED means not established in reviewed evidence, not proof no document exists.

| Load | Nominal / allowable evidence | Typical/peak demand | Startup/inrush | Connector / ground |
|---|---|---|---|---|
| Jetson host | 19 V regulated design; actual carrier range check | Complete TARK workload NOT PUBLISHED; module watts exclude peripherals | NOT PUBLISHED | DC jack, delivered polarity verify; electronics return |
| IWR1843BOOST | 5 V; supply capacity >2.5 A per TI | Actual draw NOT PUBLISHED here | NOT PUBLISHED | 2.1 mm center-positive barrel; USB return |
| B0200 | 5 V USB | M1 maximum 300 mA = 1.5 W; typical unknown | NOT PUBLISHED | Supplied USB |
| PureThermal/Lepton | 5 V USB; core via bridge only | Combined peak NOT PUBLISHED | FFC/startup characterize | USB-C/core socket |
| Each LG290P | 5 V board USB, not bare-module rail | NOT PUBLISHED | NOT PUBLISHED | USB-C; documented antenna bias only |
| BNO085 4754 | 3.3 V selected; manufacturer VIN 3–5 V | Report workload NOT PUBLISHED | NOT PUBLISHED | VIN/GND, matching SPI logic |
| ESP/wheels/buzzer | Verified board input; 3.3 V logic | Actual assembly NOT PUBLISHED | NOT PUBLISHED | Board/assembly connector verify |
| NV3 SSD | M.2 host supply | Workload demand NOT PUBLISHED here | NOT PUBLISHED | Host slot; no external feed |
| UH720 V5 | 12 V / 3.3 A adapter rating | 39.6 W supply capacity, not draw | NOT PUBLISHED | Delivered connector/polarity |
| AP V3 | 5 V / 2 A rating | 10 W capacity, not actual draw | NOT PUBLISHED | Delivered V3 connector |
| LCD/touch | 5 V input per delivered revision | Peak NOT PUBLISHED here | Backlight characterize | Avoid dual USB/power feed |
| Pi/rover B | Regulated 5 V supply | Combined node NOT PUBLISHED here | NOT PUBLISHED | Pi power input, USB rover |
| L298N/four TT | Pack/module/motor range HOLD | Paired-motor startup/stall HOLD | HOLD | Qualified terminal/crimp assembly |
| Laptop/base | Owned matched laptop PSU | Outside mobile energy sum | Per laptop | Approved mains/USB |

## Rail schedule

P = coordinated source/branch overcurrent, polarity, short-circuit, thermal/undervoltage protection, guarded terminals and strain relief. S = manual source isolation and reviewed load sequencing, never automatic motion. HOLD values require evidence before release.

| POWER_RAIL_ID | SOURCE | VOLTAGE | MAX_CURRENT | LOADS | CONVERTER | FUSE | WIRE_GAUGE_CLASS | CONNECTOR | SWITCHING | GROUND | PROTECTION | ESTIMATED_LOAD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N-R2-TRACTION+ | Owned pack after qualification | Range HOLD | Motor peaks HOLD | L298N/motors | None assumed | F-T HOLD | High-current calculated | DC rated HOLD | Independent cutoff | N-R2-TRACTION- | P/transient review | HOLD |
| N-R2-ELECTRONICS+ | Separate LiFePO4 category | Series/range HOLD | Combined peak HOLD | Regulators | Full pack range | F-E HOLD | Calculated | Keyed HOLD | Electronics master | N-R2-E-RETURN | P | Sum below |
| N-R2-C19+ | Electronics branch | 19 V target | Host budget HOLD | Jetson/SSD/direct USB | Protected DC/DC | F-C19 HOLD | Drop/ampacity calculated | Actual DC plug verify | S | OUT- verify | P | 19 I_J |
| N-R2-H12+ | Electronics branch | 12 V | Hub requirement and demand | Hub/peripherals | Buck-boost if needed | F-H12 HOLD | Calculated | Hub plug verify | S | OUT- verify | P/backfeed | 12 I_H |
| N-R2-S5+ | Electronics branch | 5 V | Radar supply >2.5 A | Radar separate input | Qualified DC/DC | F-R5 HOLD | Low-drop | TI plug | S | OUT-/USB review | P/noise | 5 I_R |
| N-R2-N5+ | Electronics branch | 5 V | AP requirement | AP | Qualified DC/DC | F-N5 HOLD | Low-drop | AP plug | S | OUT- verify | P | 5 I_AP |
| N-R2-P5+ | Peer protected source | 5 V | Pi/rover budget HOLD | Pi and rover B | Qualified supply | F-P5 HOLD | Low-drop | Pi input | Peer master | Peer return | P | 5 I_P |
| N-R2-J3V3 | Qualified host rail | 3.3 V | Header spare capacity verify | BNO085 | Host regulator | Detail review | Signal harness | Header verify | Host lifecycle | Jetson GND | No 5 V GPIO | Included in I_J |
| N-R2-ESP3V3 | Endpoint local rail | 3.3 V logic, carrier supply verify | Spare capacity HOLD | Wheels/buzzer | Board or reviewed branch | Detail review | Short harness | Board/carrier verify | Endpoint lifecycle | ESP GND | No GPIO load power | Included endpoint demand |

LCD/touch uses hub USB power only if actual revision and measured budget permit; otherwise detail a protected 5 V HMI branch within R02 without parallel VBUS feed. Base GNSS uses laptop USB; antennas use their boards; DP adapter uses interface power. All loads have a category even when a rating remains unresolved.

## Calculation and selection

I_J is complete measured 19 V host input including SSD/direct USB/IMU. I_H includes hub, thermal, rover A and assigned LCD. I_P includes Pi/rover B. Therefore P_total = 19 I_J + 12 I_H + 5 I_R + 5 I_AP + 5 I_P. Do not add downstream USB loads twice. If a device changes supply boundary, update accounting. Laptop/base is separate.

P_battery = sum(P_branch/eta_branch) + distribution loss. E_required_Wh >= P_battery × hours / usable_fraction. Ah >= E_required_Wh / nominal_pack_voltage. Unknown inputs prohibit a numeric runtime/capacity claim. M1's 100 W envelope remains PROVISIONAL, not a measured sum or certified rating.

Two-wire drop: deltaV = 2 rho L I/A at conductor temperature, plus connector drop. Select conductor from derated ampacity, drop, bundle and ambient; fuse above qualified operating demand but below wire/connector capacity with documented time-current and fault-energy clearing. Validate converter efficiency, input range, peak/transient and cooling. No arbitrary AWG/fuse/TVS is released. Motor suppression must match actual driver/freewheel hardware; no guessed component values.

## Returns and sequence

Traction return runs to its pack, not through ESP/USB wiring. Single-ended L298N inputs require an intentional ESP reference unless an approved isolation design exists. Map existing converter/USB return bonds before adding a link; no presumed isolated DC/DC. Acrylic is not a chassis ground. Retain shield practice; never lift mains protective earth.

Traction isolated → unpowered checks → qualified current-limited rails separately → hub/host/peripheral sequence per manuals → identity/health/zero-output verification. Normal shutdown closes recordings/OS before electronics removal. Emergency traction interruption remains independent. Never use L298N 5 V for Pi/Jetson/ESP. Damaged LM2596 permanently excluded.

## PROTOTYPE INDEPENDENT TRACTION POWER CUTOFF

Select accessible, latching, manually operated DC load-break hardware for verified maximum pack voltage, simultaneous motor demand and interruption conditions. F-T limits fault energy. Place it in the sole motor-energy feed and review all alternate/backfeed paths. Unknown red switch and bare JQC relay are not accepted. Not a certified E-stop.

Reset restores possible power availability, not movement. Existing ENA/ENB jumpers do not establish reset-safe inhibition; future motion needs reviewed fail-disabled enable/output circuitry and exact board binding. Local rearm plus new valid request is required after cause clearance. No auxiliary contact is invented: without verified sensing, physical-cutoff UI state is UNKNOWN, not inferred from silence.

Later tests: unpowered continuity/isolation and alternate-path review; protected low-energy output/reset/brownout checks; separately approved lifted-wheel cutoff; contained-ground coast measurement. Electrical interruption is not proof of braking.

Sources: [TI supply](https://www.ti.com/tool/IWR1843BOOST), [NVIDIA](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html), [Adafruit](https://learn.adafruit.com/adafruit-9-dof-orientation-imu-fusion-breakout-bno085/pinouts), [M1 technical register](../tark-r2-master/03_EXACT_COMPONENT_FREEZE.md). No new physical measurements.
