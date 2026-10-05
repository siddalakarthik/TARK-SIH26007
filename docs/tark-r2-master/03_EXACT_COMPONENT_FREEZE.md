# TARK R2 — exact component freeze

Revision M1 • 1 October 2026 • **Technical selections**, not purchase authorization or a wiring release.

The companion `04_FINAL_TECHNICAL_BOM.csv` is the complete component-freeze table: identity/SKU, quantity, owned/new, planning costs, both purposes, specifications, published capability, intended domain, interface, supply, host, selection rationale, cheaper/more-expensive comparisons, failure consequence, non-claims and industrial function. It also identifies sources and distinguishes physical parts from permitted category allowances. Costs below are allocated planning amounts, not live offers.

## Main exact selections

| ID | Manufacturer / exact selection | Quantity | Additional planning INR | Role |
|---|---|---:|---:|---|
| M01 | NVIDIA Jetson Orin Nano Super Developer Kit, **945-13766-0000-000**, 8 GB | 1 | 50,000 | Main local processing/recording/HMI host |
| M02 | Texas Instruments **IWR1843BOOST** | 1 | 42,500 | Primary front range/radial-motion/angular evidence |
| M03 | Arducam **B0200**, IMX291, supplied fixed M12 lens | 1 | 6,500 | Primary RGB semantics and recordings |
| M04 | Teledyne FLIR Lepton 3.5, **500-0771-01** | 1 | 19,400 | LWIR thermal contrast |
| M05 | GroupGets **PURETHERMAL-3** | 1 | 13,600 | Complete USB acquisition bridge for M04 |
| M06 | Waveshare LG290P GNSS RTK Module, **33000, RTC-battery-included kit** | 1 | 9,500 | Vehicle A rover |
| M07 | Same exact Waveshare 33000 kit | 1 | 9,500 | Physical cooperative node B rover |
| M08 | Same exact Waveshare 33000 kit | 1 | 9,500 | Fixed local correction base |
| M09 | Adafruit **4754**, BNO085 9-DOF breakout | 1 | 3,500 | Attitude, yaw-rate and acceleration evidence via SPI |
| M10 | Waveshare **11199**, 7inch HDMI LCD (C), 1024 x 600 | 1 | 5,000 | Driver HMI |
| M11 | Kingston NV3 **SNV3S/500G**, 500 GB M.2 2280 NVMe | 1 | 11,000 | Local dataset/replay storage |
| M12 | TP-Link **UH720(UN), hardware V5.0** | 1 | 3,500 | Powered USB data expansion |
| M13 | TP-Link **TL-WR902AC, hardware V3** | 1 | 2,500 | Local access point/correction and telemetry network |
| M14 | StarTech **DP2HDMI2** | 1 | 3,000 | Passive DisplayPort-to-HDMI display connection |
| M15 | UGREEN **60116 / US287**, USB-A to USB-C, 1 m data cable | 4 | 2,400 | Three GNSS links plus PureThermal link |
| M16 | Seeed Studio Grove Buzzer **107020000**, V1.1 | 1 | 750 | Low-cost audible warning, alongside visual HMI |
| M17 | Active GNSS positioning antenna supplied in each 33000 kit | 3 bundled | 0 separately | Rover A/B and base RF input; not three extra purchases |

## Explicit selection changes versus earlier Batch A

The current prompt authorizes a new technical optimization, not continuation of the old procurement gate. The earlier India/Taiwan Jetson SKU **945-13766-0007-000** is **not** being assigned the price of 0000. This M1 package explicitly selects **0000** as the technical developer-kit baseline. NVIDIA lists it for US/CA/CN/JP/PH, while 0007 is IN/TW. Regional compliance, local warranty and supplied mains lead suitability are not established for 0000 in India. Resolve those before any purchase/energization; do not silently substitute a different SKU or claim regional approval. The main compute architecture is one Orin Nano Super 8 GB, not a different processor to fit the budget. [NVIDIA SKU table](https://developer.nvidia.com/embedded/faq)

The planning anchor for the selected 0000 is the opened MG Super Labs page: INR 47,499, taxes included; allocation INR 50,000. An out-of-stock label is not an architecture failure in this task. This is not a landed quote or commitment. [Exact listing](https://mgsl.in/products/nvidia-jetson-orin-nano-super-developer-kit-67-tops)

The old active 4K adapter is replaced by DP2HDMI2 because NVIDIA documents passive **and** active DP-to-HDMI support; 4K60 is unnecessary for this panel. USB-C on the Jetson is not a display output. Exact EDID/touch operation remains a bench test. [Carrier guide](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html), [adapter](https://www.startech.com/en-ca/display-video-adapters/dp2hdmi2)

## Critical interpretation limits

| Selection | Published evidence / design choice | What must not be inferred |
|---|---|---|
| Radar | 76–81 GHz IWR1843, 3 TX/4 RX; onboard processing and documented USB-UART development path | Guaranteed obstacle range, weather immunity, full 360-degree coverage or certified collision avoidance |
| RGB | 1080p compressed video class; **100-degree diagonal** FOV, approximately 1 m-to-infinity fixed-focus range | 100-degree horizontal FOV, confirmed manual exposure/gain or reliable near-field focus. The 90–120-degree forward-view target is satisfied only in diagonal terms; characterize actual horizontal coverage |
| Thermal assembly | 160 x 120, 57-degree horizontal FOV, 8.7 Hz core; USB bridge included | Metric distance, identification at an invented range or accurate absolute temperatures without calibration/emissivity control |
| GNSS | Three RTK-capable boards, two rover roles and one base; bundled **active GNSS antenna** type is manufacturer-listed | Survey-grade antenna phase-center calibration, guaranteed all-band antenna performance, bias/connector values not reviewed, always-centimetric position |
| IMU | BNO085 gyro/accelerometer/magnetometer and fused orientation; **SPI with INT/RST** selected | A magnetometer near motors/steel gives trustworthy true heading; consumer fusion is navigation-grade INS |
| Wheel sensing | Two on-axis magnetic absolute-angle channels, AS5048A-class 14-bit SPI direction selected | Exact breakout/magnet fit or electrical harness until wheel-hub measurements and PCB review |
| Jetson | One 8 GB CUDA-capable edge developer kit | TOPS equals measured TARK FPS, all workloads already profiled, or developer-kit production qualification |
| Local network | AP + main-node Ethernet + Pi/laptop Wi-Fi, without internet dependency | Guaranteed radio range, deterministic delivery, mine-wide coverage or authenticated safety just because Wi-Fi works |

The supplied GNSS antenna is selected as part of the exact kit, not as an invented independent antenna SKU. Its full RF/phase-center specification is unresolved. Prompt 2 must preserve that limitation and verify mating/bias details before connection. No external antenna-bias injection is specified here. Antenna replacement is not budgeted as a hidden second set.

## Owned assets: identity limits are deliberate

| ID | Retained asset | Frozen role | Required before powered/mobile integration |
|---|---|---|---|
| O01 | Raspberry Pi 3 Model B+ | Node B GNSS/telemetry relay, not main AI host | Existing board/supply health and software load |
| O02 | SanDisk Ultra 32 GB microSD | O01 boot storage | Exact suffix, health and endurance; not primary dataset store |
| O03 | ESP32-S3 N16R8 / HW678-style board | Prototype local supervisory endpoint | PCB/front-back labels, USB/power interface, reserved pins; reported PSRAM is not proof of flash variant |
| O04 | HLK-LD2450 | Separate bench/reference radar | Actual device/protocol validation; no undocumented decoding in this task |
| O05 | One L298N breakout | Existing low-energy model driver | Breakout identity, paired-motor load, regulator/jumpers, thermal/current checks |
| O06 | Four yellow TT geared motors | Existing model drivetrain | Rated voltage, ratio and current specification; none invented |
| O07 | Acrylic four-wheel chassis | Existing support/vehicle | Wheel/hub geometry, payload, center of gravity and rigidity |
| O08 | Existing pack, about 7.78 V reported | Retain traction-source role only, **not cleared for use** | Chemistry, cells, capacity, protection, connector and matching charger |
| O09 | Reported 12 V approximately 1.3 Ah SLA | Bench asset, not selected mobile electronics source | Label/condition/matched charger |
| O10 | Working USB webcam, model unverified | Reference/bench camera | Exact format/model if used for quantified experiments |
| O11 | Existing laptop/control-room computer | Fixed-base USB relay and observer HMI | Ports/OS/available resources; no new laptop cost assumed |
| O12 | Existing basic wiring/fuses/switches | Inventory only | Rating and condition before any reuse; unsafe/unidentified parts do not satisfy R14/R15 |

No right-channel GPIO freeze is made. GPIO16/17 remain under investigation. No owned item receives an invented manufacturer or suffix just to fill a table.

## Allowed category freezes

- **Wheel assembly:** two noncontact on-axis magnetic angle sensors, 14-bit AS5048A-class SPI, sampled at a 100 Hz design target, with validity/error checks. Exact carrier/magnet SKU is geometry-deferred under the user's explicit exception. Required measurement deliverable: one dimensioned **left-and-right wheel-hub mounting-envelope drawing**, including shaft/hub diameter, available axial/radial clearance and achievable sensor-to-magnet gap/alignment. Do not substitute a bare IC for a finished assembly.
- **Power:** separate protected electronics battery category with matched charger; protected regulated 19 V compute branch, regulated 12 V hub branch, 5 V sensor/Pi/display branches and 3.3 V logic where appropriate. Select documented DC/DC products with short-circuit/thermal/undervoltage protections and appropriate input range. Battery capacity, converter SKUs, fuse ratings, connectors and grounding belong to Prompt 2, not this document. Existing unknown traction chemistry is not reused as a design assumption.
- **Manual interruption:** independent latching, DC load-rated traction disconnect category; not the bare relay/unrated switch, not application-controlled. Reset cannot imply a resume command. This is not a certified mine E-stop assembly.
- **Mechanics/calibration/test:** rigid mount/guard/enclosure, harness strain relief, calibration/reference fixtures and controlled-aerosol equipment allocation. No fabricated chassis dimensions or runtime claim.

## Technical source register

Manufacturer sources govern capabilities; price sources are separately recorded in the CSV and budget. Access/review date: 1 October 2026. Search-index retrieval is identified when direct retrieval was unavailable. Historical source IDs refer to unchanged `../hardware/r2-freeze/BATCH_A_SOURCE_LEDGER.md` for price-context provenance, not the new scope.

| Key | Primary technical source | Use / boundary |
|---|---|---|
| T01 | [NVIDIA FAQ](https://developer.nvidia.com/embedded/faq), [hardware](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html), [quick start](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/quick_start.html) | SKU regions, interfaces and included bench PSU; no mobile-power validation |
| T02 | [TI IWR1843BOOST](https://www.ti.com/tool/IWR1843BOOST), [SPRUIM4B](https://www.ti.com/lit/ug/spruim4b/spruim4b.pdf), [IWR1843](https://www.ti.com/product/IWR1843) | Processed UART development path; supply capacity and IC RF capability are not measured draw/range |
| T03 | [Arducam B0200](https://www.arducam.com/arducam-1080p-low-light-wdr-usb-camera-module-for-computer-2mp-1-2-8-cmos-imx291-100-degree-wide-angle-mini-uvc-spy-webcam-board-with-microphone-3-3ft-1m-cable-for-windows-linux-mac-os.html) | Fixed-lens IMX291 UVC camera, diagonal FOV and focus constraints |
| T04 | [FLIR series datasheet](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5491/Lepton_Series_7-28-23.pdf), [core identity](https://groupgets.com/products/flir-lepton-3-5) | Core capability, not finished camera weatherproofing |
| T05 | [PureThermal 3](https://groupgets.com/products/purethermal-3), [manufacturer datasheet](https://groupgets-files.s3.amazonaws.com/PT3/PT3%20Datasheet%20Rev2%20Oct%202022.pdf) | Host bridge; preserve raw/radiometric versus display distinction |
| T06 | [Waveshare product](https://www.waveshare.com/product/lg290p-gnss-rtk-module.htm), [manufacturer indexed package listing](https://www.waveshare.com/product/iot-communication/long-range-wireless/lg290p-gnss-rtk-module.htm), [Quectel module](https://www.quectel.com/product/gnss-lg290p/), [RTK note](https://quectel.com/content/uploads/2024/07/Quectel_LG290P03_RTK_Application_Note_V1.0.pdf) | Board/active-antenna package and base/rover architecture. Exact antenna RF characterization not established |
| T07 | [Adafruit overview](https://learn.adafruit.com/adafruit-9-dof-orientation-imu-fusion-breakout-bno085/overview), [pinouts](https://learn.adafruit.com/adafruit-9-dof-orientation-imu-fusion-breakout-bno085/pinouts) | SPI chosen; documented I2C problems include ESP32-S3; INT and RST required |
| T08 | [Waveshare LCD manual](https://files.waveshare.com/upload/c/cc/7inch_HDMI_LCD_%28C%29_User_Manual.pdf) | Display interface and panel; delivered revision/EDID test remains |
| T09 | [Kingston NV3](https://www.kingston.com/en/ssd/nv3-nvme-pcie-ssd) | Consumer NVMe, not power-loss-protected industrial storage |
| T10 | [UH720 V5.0](https://static.tp-link.com/upload/product-overview/2025/202505/20250520/UH720%28UN%295.0_datasheet.pdf) | Seven data ports separate from two charge-only ports; use V5 supply spec |
| T11 | [TL-WR902AC V3](https://static.tp-link.com/TL-WR902AC_V3_Datasheet.pdf) | AP/100 Mbps Ethernet, 5 V/2 A supply rating; not rugged outdoor equipment |
| T12 | [DP2HDMI2](https://www.startech.com/en-ca/display-video-adapters/dp2hdmi2) | Passive DP-to-HDMI, 1920 x 1200 class maximum; exact panel compatibility still tested |
| T13 | [UGREEN 60116](https://www.ugreen.com/tr-tr/products/tr-60116), [manufacturer NZ listing](https://nz.ugreen.com/products/ugreen-usb-a-2-0-to-usb-c-cable-nickel-plating-1m-black) | USB-A/C data, 480 Mbps class, 1 m; not a PD negotiation solution |
| T14 | [Seeed Grove buzzer](https://wiki.seeedstudio.com/Grove-Buzzer/), [SKU list](https://www.seeedstudio.com/blog/compatibility-list/) | GPIO-controlled assembled buzzer, not a bare load on MCU GPIO; no mine audibility guarantee |
| T15 | [AS5048A manufacturer page](https://www.infineon.com/part/AS5048A), [ams-origin datasheet](https://look.ams-osram.com/m/287d7ad97d1ca22e/original/AS5048-DS000298.pdf) | On-axis magnetic absolute-angle technology/SPI; no breakout or magnet SKU inferred |
| T16 | [Pi 3B+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/), [ST L298](https://www.st.com/en/motor-drivers/l298.html) | Family references only; generic owned breakout must be independently identified |

No selection is claimed physically verified by this research pass.
