# Selection decisions, competitor evidence and sources

Revision F0 · 2 October 2026

## 1. Re-evaluation record

These are engineering judgments for a bounded research workload, not results of a head-to-head hardware benchmark. The previous freeze did not control any selection.

| Function | Selected / why | Lower-cost alternative not selected | Higher-cost or different alternative not selected |
|---|---|---|---|
| Physical demonstrator | New braked, manually moved instrument cart: payload/geometry can fit the pod, with no need to invent vehicle braking performance | Old acrylic/TT assembly excluded by scope and unsuitable as the design basis | Powered UGV adds drivetrain qualification without proving HEMM stopping; borrowed vehicle is a later shadow trial |
| Main compute | Pi 5 8 GB + Hailo-8 26-TOPS HAT: bounded RGB inference with a separate CPU host for acquisition, map and evidence | Pi CPU-only or existing Pi 3B+ leaves substantially more inference-load risk | Jetson offers broader CUDA flexibility, but verified regional-price evidence is inconsistent; reject it for the costed baseline, not because it is technically inferior |
| Accelerator | Original AI HAT+ 26-TOPS variant, supported vision inference path | 13-TOPS version saves money but offers less model/concurrency margin | AI HAT+ 2's generative-AI features are not required; LLM capacity is not a mine-safety capability |
| Radar | IWR6843ISK: processed spatial/Doppler evidence and documented standalone interface, lower current price than IWR1843BOOST | LD2450 is not the desired flexible point-cloud development platform; IWRL6432BOOST is viable but low-power presence-demo tuning is not the main objective | IWR1843BOOST is viable at 76–81 GHz but costs more here; DCA1000/raw ADC acquisition is unnecessary for the defined output-level study |
| RGB | B0200: Linux UVC, documented compressed formats and fixed optics | Unknown webcam cannot anchor reproducible optical tests | OAK/stereo/global-shutter industrial cameras may add depth/timing capability, but fog stereo is not guaranteed range and current scope does not justify their cost |
| Thermal | Lepton 3.5 + PureThermal 3: open/documented acquisition and substantially more spatial samples than small thermopile arrays | MLX90640's 32×24 array suits heat sensing, not the same corroboration granularity | Higher-resolution proprietary phone thermal cameras require verified Linux/raw-data/timestamp access; Boson-class modules consume too much of this budget |
| RTK | LG290P kits ×3: affordable independent A/B/base geometry and documented RTK-capable module family | Standalone consumer GNSS cannot promise lane-level precision; two receivers omit an independent peer or the local base | ZED-F9P and survey receivers have strong ecosystems but higher complete-kit cost; no accuracy superiority is claimed merely from frequency count |
| IMU | Adafruit BNO085 via SPI: available fusion/raw-motion reports and documented board boundary | BNO055/low-cost six-axis boards are possible, but changing to them provides no compelling measurement benefit for this allocation | Navigation-grade INS or dual-antenna heading is out of budget; magnetic heading is not silently treated as equivalent |
| Wheel sensing | Two AMT102-V quadrature paths on new independently supported measurement wheels | Single wheel gives less yaw/slip disagreement information; bare optical slots require added alignment/environment work | 14-bit absolute magnetic angle adds magnet-gap/centering construction work without a requirement to know wheel angle at boot; old 14-bit freeze does not carry forward |
| MCU | Two new documented ESP32-S3 development boards; timing/acquisition and peer relay only | Old unidentified board offers no advantage to this reset | Safety PLC is not necessary for observational prototype functions and would not certify the whole experiment |
| HMI | 7-inch HDMI touch panel: dedicated visible operator station | Phone-only UI lacks a dedicated mounted driver artifact | Automotive rugged HMI/sunlight-readable larger panel deferred to industrial qualification |
| Storage | Endurance 128 GB SD, bounded sessions and laptop offload | Arbitrary consumer SD carries poorly controlled recording endurance | PCIe NVMe conflicts with the selected single-link HAT topology; USB SSD considered only if measured recording requires it |
| Network | Local AP with main node wired and peer Wi-Fi | Ad-hoc/cloud-only tethering adds internet dependence | LoRa is unsuitable for raw camera traffic and not needed for the small course; private LTE/5G belongs to mine network design |
| Power | Enclosed commercial LFP power station and original regulated supplies | DIY loose-cell pack or repurposed unknown battery increases protection/charger uncertainty | Industrial automotive DC/DC plus qualified pack is desirable for actual vehicles but not needed on a dry manual cart |
| Cutoff | Independent guarded equipment disconnect plus mechanical cart stopping | GUI stop or battery app button alone is not a physical isolation architecture | Safety-rated vehicle braking chain is a separate OEM/site engineering program, not a decorative relay on this cart |
| Mechanics | Removable rigid pod, low battery, protected wiring, accessible service panels | Improvised mast and exposed jumper wires compromise repeatability | Premium enclosure/IP claims without thermal/RF/LWIR testing are not purchased credibility |
| Control room | Shared laboratory laptop/access: commodity browser/server workload, no AI workstation needed | Depending entirely on the driver display fails the separate control-room demonstration | Dedicated GPU control-room computer wastes edge-compute duplication in a two-node prototype |

## 2. Compute decision and price conflict

The selected Pi package is allocated INR 34,700 including accelerator, cooler and official supply. Current opened board pricing was INR 20,349; the HAT listing showed INR 10,989. These are not the much lower Raspberry Pi prices from earlier years.

The NVIDIA path was genuinely reconsidered. NVIDIA identifies 945-13766-0007-000 for IN/TW and describes developer kits as pre-production tools. The opened MG Super Labs listing priced **0000** at INR 47,499, out of stock. A RoboTechMinds search excerpt displayed INR 33,600 for **0007**, but its opened category page displayed **INR 68,000**. The cheaper indexed excerpt was not adopted as a verified offer. At INR 68,000, replacing the Pi package alone adds INR 33,300 before any display/power accessories and breaks this allocation. [NVIDIA regions](https://developer.nvidia.com/embedded/faq), [MG listing](https://mgsl.in/products/nvidia-jetson-orin-nano-super-developer-kit-67-tops), [conflicting retailer page](https://www.robotechminds.com/category/nvidia)

This is not “26 TOPS is equivalent to 67 TOPS.” Models, numerical precision, host load and runtimes differ. Selection requires a supported compiled vision model and a measured end-to-end pipeline, not a TOPS comparison. Hailo does not accelerate arbitrary Python, tracking, map rendering or unsupported networks. UVC capture is not automatically integrated by the Raspberry Pi camera examples. Failure of the integration gate must be reported, not hidden by a CPU-only demo labelled accelerated.

## 3. Competitor evidence boundary

Reviewed local research: [prior competitor register](../tark-r2-master/01_COMPETITOR_CAPABILITY_MATRIX.md) and the recorded description-review basis it cites. That material records inaccessible videos; **this redesign does not claim to have watched those videos or verified their operation**. No new ranking or timestamped footage comparison is asserted.

| Proposal group in prior record | Description-level claim | Consequence for TARK |
|---|---|---|
| MineSafe | Moving model, ultrasonic/fog indication, driver display | A moving chassis plus alarm is not distinctive |
| DRISHTI | AI/proximity, GPS/V2V, dashboard | Tracking and a dashboard are baseline ideas |
| PROXIMINE / SafePit | Ultrasonic arrays, ESP-NOW, OLED, stop threshold | Wireless peer messages and threshold stops are not sufficient novelty |
| MINE VISION | Multimodal sensing, mesh, corridor/HUD | Multisensor integration alone is not a differentiator |
| Infranova / FogGuard | Radar/LiDAR/camera, environment/GNSS, network/control room | Do not market a sensor shopping list as unique |
| FogX / SmartMine FogGuard | Radar/LiDAR/thermal/GPS/V2X concepts | Thermal and cooperative awareness overlap existing proposals |
| Vinay Sing, SD creation, TRINETRAM | Insufficient accessible operation evidence | Unknown means unknown, never “they lack this feature” |

For each comparator the source URLs and access limitations remain in that register. All performance comparisons require new accessible evidence. TARK can defensibly propose deeper tests without claiming that others have not done them.

## 4. Demonstrable differentiation

| Proposition | Hardware implication | Demonstration that earns the claim |
|---|---|---|
| Evidence has a validity interval | Stable acquisition clocks and retained device/host timing | Delay a stream; show it expires rather than remaining green |
| Disagreement is retained | Independent RGB, LWIR and radar evidence | Present warm non-person/static reflector cases; display conflicting evidence instead of forced fusion |
| Localization has uncertainty | Base, two rovers and measured lever arms | Lose corrections; display degraded position and suppress precise lane/turn assertions |
| Hidden-vehicle conflict uses cooperation | Real node B, not a generated dashboard marker | Receive B behind visual occlusion; then break its link and show uncertainty/staleness |
| Decisions are auditable | Local storage of raw/normalized evidence and parameter identity | Select an event and reconstruct inputs, rejected inputs, constraints and state changes |
| Offline local operation | Local AP, storage and course graph | Remove internet without removing local functions; distinguish local-network loss separately |
| Industrial mapping is honest | Removable pod, separate shared infrastructure | Explain what is per vehicle and what still requires automotive/mine qualification |

## 5. Technical source ledger

Retrieved/read in this redesign unless marked retained. Manufacturer sources support specifications; retailer descriptions are not substituted for manufacturer interface drawings. A blocked download stays blocked.

| ID | Source | Supported decision / caveat |
|---|---|---|
| S01 | [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) | Host platform/interface family; actual combined workload remains unmeasured |
| S02 | [Official AI HAT+](https://www.raspberrypi.com/products/ai-hat/) and [AI HAT documentation](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html) | Select original 26-TOPS Hailo-8 variant, not generative HAT+ 2 |
| S03 | [27 W supply](https://www.raspberrypi.com/products/27w-power-supply/) | Proper Pi supply; regional plug must be checked |
| S04 | [NVIDIA Orin Nano Super](https://www.nvidia.com/en-in/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/) and [FAQ](https://developer.nvidia.com/embedded/faq) | Rejected compute comparison; regional SKU and non-production developer-kit boundary |
| S05 | [TI IWR6843ISK](https://www.ti.com/tool/IWR6843ISK) | Standalone processed point-cloud interface, antenna family; no raw-ADC board needed |
| S06 | [TI SWRU546E guide](https://www.ti.com/lit/ug/swru546/swru546.pdf) | Revision-specific standalone/power instructions, handling and EVM use restrictions; exact profile/power still to freeze |
| S07 | [TI area-scanner reference](https://www.ti.com/lit/ug/tiduei1c/tiduei1c.pdf) | Example profile parameters are configuration-specific, not universal sensor guarantees |
| S08 | [Arducam B0200](https://www.arducam.com/arducam-1080p-low-light-wdr-usb-camera-module-for-computer-2mp-1-2-8-cmos-imx291-100-degree-wide-angle-mini-uvc-spy-webcam-board-with-microphone-3-3ft-1m-cable-for-windows-linux-mac-os.html) | Exact optics, formats and power; do not substitute a family lens silently |
| S09 | [FLIR Lepton data](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5491/Lepton_Series_7-28-23.pdf) and [GroupGets PT3](https://groupgets.com/products/purethermal-3) | Thermal core identity and USB bridge; original source data retained from earlier research plus PT3 re-opened |
| S10 | [Waveshare LG290P page](https://www.waveshare.com/product/lg290p-gnss-rtk-module.htm) and [wiki](https://www.waveshare.com/wiki/LG290P_GNSS_RTK_Module) | Manufacturer pages failed direct retrieval in this pass; exact kit evidence from P07; UART electrical release remains pending |
| S11 | [Quectel LG290P RTK application note](https://quectel.com/content/uploads/2024/07/Quectel_LG290P03_RTK_Application_Note_V1.0.pdf) | Retained primary-source reference for base/rover design; firmware/version/commands must be locked before integration |
| S12 | [Adafruit BNO085 pinouts](https://learn.adafruit.com/adafruit-9-dof-orientation-imu-fusion-breakout-bno085/pinouts) | SPI, INT/RST and mode straps; 3.3 V system choice |
| S13 | [Same Sky AMT102-V](https://www2.sameskydevices.com/product/motion-and-control/rotary-encoders/incremental/modular/amt102-v) | Quadrature kit, configurable PPR and shaft sleeves; no absolute-angle claim |
| S14 | [TI SN74LVC2G17](https://www.ti.com/product/SN74LVC2G17) | 5-V-tolerant inputs and 3.3 V output-supply design; carrier protection still to design |
| S15 | [Espressif DevKits](https://www.espressif.com/en/products/devkits/esp32-s3-devkitc-1/overview) | Documented new board family; physical delivered board must match exact ordered variant |
| S16 | [SanDisk MAX Endurance](https://www.sandisk.com/en-in/products/memory-cards/microsd-cards/sandisk-max-endurance-uhs-i-microsd?sku=SDSQQVR-128G-GN6IA) | Selected recording medium; surveillance endurance rating is not a database power-loss guarantee |
| S17 | [TP-Link UH720 V5 data](https://static.tp-link.com/upload/product-overview/2025/202505/20250520/UH720%28UN%295.0_datasheet.pdf) and [AP V3 data](https://static.tp-link.com/TL-WR902AC_V3_Datasheet.pdf) | Retained primary hardware-version references; no mine RF coverage claim |
| S18 | [Waveshare display manual](https://files.waveshare.com/upload/c/cc/7inch_HDMI_LCD_%28C%29_User_Manual.pdf) | Retained identity/interface reference; exact display power/touch cable revision remains a gate |
| S19 | [EcoFlow RIVER 2](https://www.ecoflow.com/uk/river-2-portable-power-station) | Product family energy/power/BMS; UK/US plugs are NOT authorization for the India unit |
| S20 | [Waveshare UGV01](https://www.waveshare.com/product/robotics/mobile-robots/ugv01.htm) | Powered-platform alternative considered, not selected |
| S21 | [Grove buzzer](https://wiki.seeedstudio.com/Grove-Buzzer/) | Retained interface reference; not a certified cab alarm |

## 6. Price evidence ledger

Price date: 2 October 2026 for re-opened/retrieved results. Retained anchors are explicitly marked and are allocations, not new checkout verification.

| ID | Listing | Observation |
|---|---|---|
| P01 | [Hubtronics Pi 5 8 GB](https://hubtronics.in/raspberry-pi-5-8gb) | Opened: 20349 incl GST; page also lists official cooler 560 and supply 1275. Old related-kit price was not used |
| P02 | [Hubtronics AI HAT+ 26](https://hubtronics.in/raspberry-pi-store/hats-for-raspberry-pi/official-raspberry-pi-ai-hat-plus-26tops) | Retrieved listing: 10989 incl GST; out of stock |
| P03 | [Mouser IWR6843ISK](https://www.mouser.in/en/ProductDetail/Texas-Instruments/IWR6843ISK?qs=sGAEpiMZZMuEyVOlQDISiqS7hNiRrljro6%252BV0iTB3Tz57cR4z%252BbVKQ%3D%3D) | Retrieved 26895.48; tax/fees not confirmed |
| P04 | [Fab.to.Lab B0200 family](https://www.fabtolab.com/arducam-b0200-b0201-b0202-1080p-low-light-wide-angle-usb-camera-module-microphone-computer-2mp-1-2-8-inch-cmos-imx291-120-degree-mini-uvc-usb2.0-webcam-board-3-3ft-1m-cable-windows-linux-mac-os) | Prior-day 5262 anchor retained, not re-verified; B0200 exact optics required |
| P05 | [DigiKey Lepton](https://www.digikey.in/en/products/detail/flir-lepton/500-0771-01/7606616) | Opened price table 16434.60 |
| P06 | [DigiKey PT3](https://www.digikey.in/en/products/detail/groupgets-llc/PURETHERMAL-3/18677153) | Opened price table 11465.04 |
| P07 | [Hubtronics Waveshare 33000](https://hubtronics.in/lg290p-gnss-rtk-module) | Opened 9099 incl GST, out of stock; antenna and RTC battery listed in package |
| P08 | [Mouser AMT102-V](https://www.mouser.in/en/ProductDetail/Same-Sky/AMT102-V?qs=WyjlAZoYn533PQfgnorrMg%3D%3D) | Retrieved 2888.58 each; tax not confirmed |
| P09 | [Hubtronics display](https://hubtronics.in/7inch-hdmi-lcd-c) | Prior-day 4479 inclusive anchor retained |
| P10 | [Moglix UH720](https://www.moglix.com/tp-link-7-port-usb-30-data-hub-with-2-port-smart-charger-uh720/mp/msnm9xy2zj7mkj) | Prior-day 2905 inclusive anchor retained; revision not proved by price |
| P11 | [Flipkart AP](https://www.flipkart.com/tp-link-tl-wr902ac-750-mbps-router/p/itmf47djfhyzrhzf) | Prior-day 2099 anchor retained; fees/revision not fixed |
| P12 | [EcoFlow India listing](https://ecoflowindia.com/collections/river-series-2/products/ecoflow-river-2-portable-power-station-256wh) | Retrieved 29990; verify seller, regional label and complete warranty terms before purchase |

Prices do not validate safety, sellers, authenticity, regional compliance, exact connector pinouts or performance. F0 is a costed technical proposal with explicit release gates, not a purchase recommendation to bypass those gates.
