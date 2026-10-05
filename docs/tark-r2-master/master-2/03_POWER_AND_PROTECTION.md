# Master-2 — power and protection design

**Parameterized electrical design. No final fuse, battery, converter, connector or conductor rating is invented. Do not energize from this document.** M1's protected-power allocation remains INR 18,000; unspent budget is reserve, not authority to add equipment.

## 1. Planned energy topology

```text
TRACTION ENERGY DOMAIN (owned pack identity/protection still HOLD)
  traction source positive -> source protection -> rated manual DC disconnect
                           -> protected driver supply -> L298N -> TT motors
  dedicated high-current return -------------------------------> source negative

ELECTRONICS ENERGY DOMAIN (protected LiFePO4 category + matched charger)
  source protection -> electronics service disconnect -> protected distribution
     +-> regulated 19 V branch -> Jetson (including its direct USB loads and SSD)
     +-> regulated 12 V branch -> UH720 (including hub-powered peripherals)
     +-> regulated 5 V radar branch -> IWR1843BOOST external input
     +-> regulated 5 V AP/display auxiliary branches as actually required
  local 3.3 V logic/IMU supply within documented host/breakout limits

PEER / BASE
  Pi B + rover B: separately qualified regulated 5 V source
  base + laptop: laptop's qualified supply/USB path
```

This expresses separate energy branches, **not proven galvanic isolation**. Local signal references must be compatible; common returns can join otherwise separate battery domains. The old R1 12 V/MDD10A/contactor schematic is not silently reused for this L298N model. Use R2-prefixed working net labels until a reviewed drawing is issued.

| Logical net | Meaning | Release status |
|---|---|---|
| R2_TRACTION_BAT_POS / NEG | Actual verified traction source terminals | Polarity/range/chemistry HOLD |
| R2_TRACTION_SWITCHED | Downstream of independent manual traction disconnect | Switch/fuse/connector ratings HOLD |
| R2_ELECTRONICS_IN / RETURN | Protected electronics source input/return | Pack/charger and source rating HOLD |
| R2_19V / RETURN | Jetson regulated branch | Exact converter, current/polarity and inrush review HOLD |
| R2_12V / RETURN | Powered USB hub branch | Converter/ripple/load review HOLD |
| R2_5V_RADAR / RETURN | Radar external power branch | Documented EVM supply requirements govern |
| R2_5V_AUX / RETURN | Individually accounted auxiliary loads | Actual display/AP/peer topology and ratings HOLD |
| R2_LOGIC_REF | Reviewed common low-current signal reference | Bonding/alternate USB paths must be drawn and tested |

## 2. Load accounting without double counting

The M1 **100 W regulated-output envelope is a provisional sizing target**, not measured consumption or an accepted converter rating. It must be reconciled against simultaneous worst-case loads before mobile-power release.

| Load group | Boundary for measuring/budgeting | Information that must be obtained |
|---|---|---|
| P_J | Jetson DC input including SSD, RGB and directly powered ESP32/IMU loads | Boot peak, inference/recording/display load, thermal mode; module-only power is insufficient |
| P_H | Hub DC input including thermal, rover A and USB touch/power actually supplied | Hub efficiency, charging-port prohibition for data, peripheral peak/FFC behavior |
| P_R | Radar external 5 V input | Configured EVM demand, startup and USB power interaction |
| P_A | AP regulated input | AP peak/current and voltage drop |
| P_D | Display auxiliary supply **only if not already in P_H/P_J** | Actual board's power scheme; avoid dual feed/backfeed |
| P_B | Pi B plus rover B supply | Separate source/load budget; not presumed free from main pack |

Main electronics output budget is `P_J + P_H + P_R + P_A + P_D`, where each downstream load appears exactly once. Peer power is accounted separately in the same project power allocation. Converter input power is `sum(P_branch / eta_branch)` plus upstream losses; do not add every downstream USB device again.

Published PSU capacities are compatibility/sizing references, **not actual consumption**. The hub V5.0 supply specification is 12 V/3.3 A; the AP V3 specifies 5 V/2 A; the radar guide requires a 5 V source with capacity above 2.5 A. Summing these supply maxima with an arbitrary Jetson estimate is not a validated load test. NVIDIA specifies a shared VBUS limit per dual-stacked USB-A pair; distribute loads only after checking the actual topology. [NVIDIA hardware](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html), [TI guide](https://www.ti.com/lit/ug/spruim4b/spruim4b.pdf), [hub V5](https://static.tp-link.com/upload/product-overview/2025/202505/20250520/UH720%28UN%295.0_datasheet.pdf), [AP V3](https://static.tp-link.com/TL-WR902AC_V3_Datasheet.pdf)

## 3. Converter and battery specification method

For each converter, record delivered part/revision, input operating range, regulated output tolerance/ripple, continuous and transient load rating at actual enclosure temperature, efficiency curve, protection behavior, reverse-current/backfeed behavior and connector polarity. The full battery terminal range—including sag and charger-connected cases if permitted—must remain within the converter's qualified input range.

Use regulation appropriate to that range: a boost-only 19 V solution is valid only if its whole input range is below the output and protection requirements are satisfied; a 12 V branch may need buck-boost if the battery crosses 12 V. Do not infer a regulator topology from its marketing wattage. Choose only documented protected products within R02; exact part selection remains gated by actual load/battery data rather than a fictitious universal module.

Battery energy sizing:

`E_nominal_Wh >= P_average_W * runtime_hours / (eta_system * usable_fraction)`

Peak current sizing is separate: `I_input_peak >= P_output_peak / (V_input_min * eta_min)`, with documented transient margin and battery/BMS compatibility. The pack's mass and discharge capability also constrain the chassis. No runtime, Ah or charger voltage is released here. The owned pack's 7.78 V reading does not identify its chemistry, safe charger or protection state. The separate SLA remains a bench asset, not a substitution for the electronics category.

Do not combine unknown packs, bypass BMS protection, or charge through improvised converters. Keep charging outside the motion experiment unless a separately reviewed power-path design permits it. A matched charger is a selected-pack requirement, not an assumed property of an existing adapter.

## 4. Protection and return-path requirements

Source protection is near the source; branch protection limits conductor/connector fault energy. A fuse must carry the real derated normal load and permitted startup current, yet protect the weakest downstream conductor/component using its time-current/I-squared-t curve. DC voltage and interrupt ratings must cover the actual pack and prospective fault current. Do not choose a fuse merely from motor running current or nominal battery voltage.

Wire drop calculation for a two-conductor circuit is `delta_V = 2 * L * rho * I / A`, with actual length, material, cross-section and temperature corrections. Verify ampacity, connector contacts, crimp/solder quality, flex and bundling separately. Wire heating is `I^2 * R`. No generic AWG value is released before these inputs exist.

Planned low-voltage signal architecture uses a documented common reference where required by the nonisolated control interface, with motor return currents routed directly to the traction source, not through an ESP32, USB shield or signal ground. Draw every negative/return and bond explicitly. If any chosen converter is isolated, its secondary return/bond must be treated explicitly; never assume its input/output negatives are common. Do not parallel converter outputs or regulator outputs.

Check alternate paths through USB shields/grounds, laptop power, programming cables, display cables and chargers. Prove that opening the traction disconnect removes all paths capable of energizing the motor bridge supply. The fact that two packs are separate is not proof of that result.

The L298N module's onboard 5 V regulator is not a Pi/Jetson/ESP32 supply. Its regulator jumper, logic-supply behavior, flyback protection and input thresholds must be established from the actual breakout. The damaged LM2596 remains permanently excluded.

## 5. Independent interruption versus command stop

The manual DC-rated traction disconnect is independent of Jetson, browser, AP and ESP32 firmware. Electronics should normally remain powered long enough to report the interruption; a separate service disconnect provides full de-energization. Resetting a physical device must not resume motion or replay an old command.

Opening traction power can cause **coasting**, not controlled braking. Do not label the prototype disconnect as a mine-certified emergency-stop system. Stopping/coasting distance and restoration behavior require measured tests with a restrained low-energy setup and competent electrical review.

Driver enable is distinct from disconnect. Existing ENA/ENB jumpers are reported installed; pins may be undefined during reset. A future motion-enabled design requires a reviewed passive default-disabled enable/output arrangement, independent of post-boot software initialization. Final GPIOs/components cannot be assigned until the exact board/module is verified. ST's IC enable behavior does not prove the generic breakout's complete behavior. [ST L298](https://www.st.com/content/st_com/en/products/motor-drivers/brushed-dc-motor-drivers/l298.html)

## 6. Release sequence — future authorized work only

Unpowered identity/continuity/polarity review → documented source and regulator testing without sensitive loads → branch load/inrush/thermal tests → USB/backfeed/return-path tests → compute/sensor-only integration with traction physically disconnected → separately authorized restrained driver tests. Current M2 work performs none of these.

A detailed wiring/fabrication release is blocked until the actual pack/charger, branch loads, exact converter/fuse/disconnect/connector ratings, power returns and boot-disable behavior are documented. This hold does not reopen the frozen sensing or compute architecture.
