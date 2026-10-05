# Components and cost-controlled BOM

Revision F0 · Currency INR · Research checked 2 October 2026

The rows below are the single cost ledger for this design. **Exact commercial parts and custom assemblies are intentionally distinguished.** An allocation does not imply an assembled product exists at that price. Source references Sxx/Pxx resolve in [the source ledger](03_DECISIONS_AND_SOURCES.md).

Classification: **V** = per-vehicle function, with industrial replacement/qualification; **P** = prototype/test equipment only; **S** = shared infrastructure. Mixed rows state their split. All listed purchases are new; none rely on old hobby-robot components.

## 1. Quantities and planning allocations

| ID | Selected manufacturer / model / identity | Qty | Unit INR | Extended INR | Class | Price basis |
|---|---|---:|---:|---:|---|---|
| F01 | Raspberry Pi Ltd, Raspberry Pi 5, **8 GB**; retailer SKU 05098 is not a manufacturer part number | 1 | 21000 | 21000 | V | P01: 20349 incl GST, rounded |
| F02 | Raspberry Pi **AI HAT+ 26 TOPS / SC1791**, Hailo-8, not AI HAT+ 2 or 13-TOPS variant | 1 | 11500 | 11500 | V | P02: 10989 incl GST, rounded |
| F03 | Official Raspberry Pi 5 Active Cooler | 1 | 700 | 700 | V | P01: 560, mounting clearance allowance |
| F04 | Official Raspberry Pi 27 W USB-C supply; India-compatible plug variant to confirm | 1 | 1500 | 1500 | P | P01: 1275; regional suffix not guessed |
| F05 | Texas Instruments **IWR6843ISK**, standalone-capable current board revision, not ISK-ODS/AOP | 1 | 32000 | 32000 | V | P03: 26895.48 before unconfirmed tax treatment; approximately ×1.18 rounded |
| F06 | Arducam **B0200** IMX291 USB camera with supplied lens/cable | 1 | 6500 | 6500 | V | P04 family price anchor 5262 from prior research; allowance, exact variant quote pending |
| F07 | Teledyne FLIR Lepton 3.5 **500-0771-01** | 1 | 19400 | 19400 | V | P05: 16434.60; tax provision rounded |
| F08 | GroupGets **PURETHERMAL-3**, Lepton USB bridge | 1 | 13600 | 13600 | V | P06: 11465.04; tax provision rounded |
| F09 | Waveshare **33000** LG290P kit, active antenna and RTC battery included | 3 | 9500 | 28500 | 2 V, 1 S | P07: 9099 incl GST each; A/B/base |
| F10 | Adafruit **4754 BNO085** breakout | 1 | 3500 | 3500 | V | Prior distributor anchor; planning allowance, not new quote |
| F11 | Same Sky, formerly CUI Devices, **AMT102-V** incremental encoder kits | 2 | 3500 | 7000 | V/P | P08: 2888.58 each; tax provision rounded |
| F12 | Espressif **ESP32-S3-DevKitC-1-N8**, official documented board, no old HW678 assumed | 2 | 1500 | 3000 | V/P | Engineering estimate; one measurement MCU A, one bridge MCU B |
| F13 | Two **TI SN74LVC2G17DBVR** buffers plus small protected 3.3 V interface assembly and passive parts | 1 lot | 1000 | 1000 | V/P | Engineering estimate; not a released PCB |
| F14 | Waveshare **11199**, 7inch HDMI LCD (C), 1024×600 touch display | 1 | 5000 | 5000 | V | P09: previous 4479 incl GST anchor; current quote pending |
| F15 | SanDisk MAX ENDURANCE **SDSQQVR-128G-GN6IA**, 128 GB microSD | 1 | 3000 | 3000 | V | Planning allowance, not a retrieved live INR quote |
| F16 | TP-Link **UH720(UN) V5.0** powered USB hub, supplied adapter | 1 | 3500 | 3500 | P | P10 prior 2905 anchor; exact revision/contents pending |
| F17 | TP-Link **TL-WR902AC V3** local access point/router, supplied adapter | 1 | 2500 | 2500 | S | P11 prior 2099 anchor; exact revision pending |
| F18 | Data/HDMI/Ethernet cable set, including Pi micro-HDMI cable, suitable radar USB cable and strain relief | 1 lot | 3500 | 3500 | Mixed | Engineering estimate; cable schedule in document 04 |
| F19 | Seeed Studio Grove Buzzer **107020000**, with compatible interface lead | 1 | 750 | 750 | V | Engineering estimate; verify acoustic adequacy |
| F20 | EcoFlow **RIVER 2, EFR600 family**, 256 Wh; **India 230 V / 50 Hz variant** required | 1 | 30000 | 30000 | P | P12: 29990; region label/packaging must match |
| F21 | Custom **TARK-F0-CART** assembly: braked cart, two instrument-wheel axles, mast, sensor plate, dry enclosures, guards and fasteners | 1 | 15000 | 15000 | P | Fabrication allowance, NOT a commercial SKU or completed structural design |
| F22 | Protected 5 V USB power-bank package for node B, minimum 10 Wh usable energy and 2 A rated output; charger/lead included | 1 | 1500 | 1500 | P | Procurement specification; exact reputable maker/model not selected |
| F23 | Professionally assembled guarded power-distribution/cutoff package: approved power strip, mechanical all-pole disconnect, required branch protection, auxiliary USB supply | 1 | 5000 | 5000 | P | Assembly allowance; exact protective devices depend on regional unit and inspection |
| F24 | Fixed GNSS base tripod/antenna mount + separate node-B pole/carrier | 1 lot | 2000 | 2000 | S/P | Workshop allowance; antenna elements already in F09 |
| F25 | Calibration/reference fixtures and laboratory instrument access | 1 lot | 5000 | 5000 | S | Includes reflector, charts, measured markers and access; not purchase of survey equipment |
| F26 | Supervised low-visibility test setup/access, approved fluid/equipment rental and cleanup | 1 lot | 3000 | 3000 | S | Experimental allowance; no homemade chemical formulation |
| F27 | Laboratory control-room laptop/access allocation for the demonstration period | 1 | 3000 | 3000 | S | Access/loan contingency, **not purchase of a laptop** |

| Reconciliation | INR |
|---|---:|
| Sum F01–F27 | **231950** |
| Unspent price/integration reserve | **15000** |
| Total planning allocation | **246950** |
| Approved ceiling used | **250000** |
| Further unallocated headroom | **3050** |

No estimated tax provision is described as an actual tax invoice. Do not add GST twice where listings already include it. Unknown shipping/import costs draw on reserve; they are not claimed zero. No orders or delivery optimization were performed.

## 2. Specifications, domain and integration requirements

| ID | Specification and role | Usable domain / limitation | Interfaces and supply | Mechanical requirement |
|---|---|---|---|---|
| F01–F04 | 8 GB Linux host, CPU services plus dedicated Hailo inference; active cooling | One forward vision pipeline, thermal handling, radar/location/replay target; simultaneous performance unmeasured | HAT uses PCIe; host uses official 5.1 V/5 A capable USB-C supply; HDMI/USB/Ethernet | Vented rigid mount, cooler airflow, clearance for stacked HAT; not a sealed hot box |
| F05 | 60–64 GHz, 3 TX/4 RX processed point-cloud evaluation platform | Forward controlled-course geometry/Doppler; antenna FoV is not guaranteed detection coverage | USB serial configuration/data in supported standalone mode; profile-dependent power verified before use | Rigid calibrated boresight, clear antenna aperture; no metal cover in beam |
| F06 | 2 MP IMX291; vendor lists H.264/MJPG/YUY2; 100° **diagonal** lens | Visible-light semantics at calibrated ranges, not fog penetration; near focus about 1 m | UVC USB 2; 5 V, manufacturer max 300 mA | Small lens hood and rigid mount; lens/board must not rotate after calibration |
| F07–F08 | 160×120 thermal core + Linux-capable UVC bridge, approximately 8.7 Hz core | Thermal contrast corroboration, not independent distance or guaranteed identity | USB-C into bridge; core rails generated by bridge, never apply 5 V directly to core | Unobstructed LWIR aperture; ordinary glass/acrylic is not a transparent LWIR window |
| F09 | Three quad-band RTK-capable kits and their supplied active antennas | Open-sky relative/absolute position only when quality and reference justify it | A and base use USB 5 V; B uses board's documented UART after logic-level review; RTCM return path required | Fixed base, repeatable antenna reference points, known rover lever arms and restrained coax |
| F10 | Gyroscope, accelerometer, magnetometer/fusion device | Motion/yaw-rate evidence; not a navigation-grade INS or dependable magnetic north near steel | Select 3.3 V supply/logic, SPI with separate CS/INT/RST via measurement MCU | Rigid close-to-body-reference mount, away from power box; axes recorded |
| F11 | Capacitive incremental quadrature encoders; selectable 48–2048 PPR; target 1024 PPR | Two wheel responses and yaw plausibility; slip/lift invalidates distance | Regulated 5 V within published 3.6–5.5 V range; A/B level-conditioned to 3.3 V | Independent bearings carry wheel load; encoder is not an axle bearing; shaft sleeve selected for NEW assembly |
| F12–F13 | MCU A timestamps wheel/IMU observations; MCU B relays GNSS/RTCM | Monitoring only; both boards are development hardware | USB 5 V and 3.3 V logic; buffer input accepts 5 V, output at 3.3 V; no direct 5 V into MCU | Secured protected carrier, short internal signals and connector strain relief |
| F14, F19 | Driver touch display + audible attention cue | Readable dry demonstration; not outdoor cab brightness or alarm certification | HDMI video; separate supported 5 V display power/touch arrangement; buzzer interface checked before use | Push-handle display bracket, no obstruction of operator view or sensor field |
| F15 | 128 GB endurance-oriented microSD, bounded recorder and boot storage | Student test sessions; no enterprise power-loss protection or indefinite retention | Native SD interface; no PCIe contention with accelerator | Accessible only while safely shut down; maintain separate dataset backup |
| F16 | Powered USB fan-out | Desktop development accessory, not automotive hub | Supplied adapter; only data ports carry sensor links; charge-only ports are not data ports | Retention clips and strain relief; verify no backfeed and realistic port-current distribution |
| F17 | Local Wi-Fi AP plus Ethernet, no cloud dependency | Small validated test area; not mine-wide RF coverage | Ethernet to main node, Wi-Fi to node B/laptop; supplied regulated power | Central dry location, antennas unobstructed; no internet required after setup |
| F18 | Short documented interconnects | Data integrity, not just connector mating | No charge-only cables on data paths; no passive Y power combiners | Label both ends; protected routing and service loops |
| F20 | 256 Wh LFP power station, nominal 300 W AC class | Dry controlled test equipment; not mine vehicle power conditioning | Use approved regional AC output and vendor adapters; internal pack/BMS/charger untouched | Low on cart; restrained with ventilation and reachable controls |
| F21 | New human-operated load-support platform | Level, segregated course; initial speed limit ≤1 m/s | No motor, ESC, H-bridge or software brake output | Service/parking brake, non-tip layout, wheel guards, removable pod |
| F22 | Protected USB source | Node B only, with low-load shutdown tested | Dedicated USB power; no charging while moving; no paralleled USB outputs | Enclosed carried fixture, covered connectors |
| F23 | Equipment isolation, distribution and protective devices | Electrical fault response only, NOT a cart brake | All-pole isolation appropriate to inverter topology; no invented neutral-earth bond | Guarded professional assembly; all exposed mains inaccessible |
| F24–F27 | Base geometry, repeatable targets, laboratory and control-room access | Shared experimental resources | Laptop USB to base and Wi-Fi to AP; other instruments only as qualified | Stable tripod, secured course, separate wet/aerosol and electrical areas |

Each V-class item represents an industrial **function**, not approval to bolt that exact development board onto a dumper. Industrial replacements are described in document 05.

## 3. Why storage is smaller than the old plan

The budget buys useful measurement capability before speculative long-term retention. The AI HAT occupies the Pi's PCIe connection; this design does not quietly install a conflicting NVMe HAT. The selected endurance microSD supports bounded acquisition with offload to the laboratory laptop.

Illustrative allocation: 40 GB OS/models, 20 GB free-space/maintenance margin, 60 GB bounded dataset space. These decimal allocations total 120 GB and leave nominal capacity headroom; actual formatted usable capacity must be checked. An **assumed**, not measured, 8 Mb/s compressed RGB stream uses 3.6 GB/h. Uncompressed 16-bit thermal at 160×120×8.7 Hz is about 1.203 GB/h. An assumed 0.5 MB/s metadata/radar budget adds 1.8 GB/h. Total example 6.603 GB/h; 60 GB gives about 9.1 hours before overhead. Larger actual streams reduce retention.

Use camera-supported compressed capture without claiming simultaneous multi-format streams. Decode/preprocess load on the Pi still needs measurement. Do not overwrite locked incident records silently. A USB SSD is a later justified response to measured endurance/throughput failure, not an automatic purchase from the reserve.

## 4. Cost honesty and alternatives

- The budget is a **new flagship allocation**. No unverified hobby battery is counted as a free qualified supply.
- It includes physical node B, three RTK antennas through their kits, and a fixed base; those are not missing extras.
- It does not buy a new control-room laptop, oscilloscope, total station or traceably calibrated thermal blackbody. F25/F27 require confirmed laboratory access. Their purchase is outside this ceiling unless the BOM is rebalanced.
- F21 and F23 need fabricator/electrical-review quotations. Their exact geometry, ratings and protective-device SKUs remain open; no fabrication-ready claim is made.
- Student engineering/software labour, mine vehicle, actual mine survey, formal certification, industrial enclosure qualification, mine RF installation and fleet rollout are excluded.
- Listed out-of-stock research anchors are prices, not availability promises. No delivery date is promised.
- A 10% rise in the base allocation is INR 23,195, exceeding the INR 18,050 combined reserve/headroom by INR 5,145. Reconcile quotes before spending; never remove protection or mislabel a lower-quality sensor to force a fit.

## 5. Budget release rule

Release no purchase until exact SKU/package content, valid price/taxes, mechanical/power compatibility and laboratory-access assumptions are recorded. The planning target stays INR 231,950 before reserve; unused money stays unspent. If essential verified costs exceed INR 250,000, report that fact and revise scope openly rather than claim the budget still fits.
