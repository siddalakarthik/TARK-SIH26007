# TARK R2 — component decision log

Revision M1 • Decisions are for technical fit, not supplier logistics.

| Decision | Selection and reasoning | Cheaper alternative rejected for this role | More expensive alternative not needed |
|---|---|---|---|
| D01 Main compute | One Orin Nano Super 8 GB handles intended CUDA perception plus local acquisition/recording. Actual concurrent workload must be profiled | Pi 3B+ retained for telemetry, not assumed capable of flagship multi-stream AI | Orin NX/AGX or second Jetson has no measured workload justification yet |
| D02 Regional SKU | Explicitly choose 945-13766-0000-000 in M1 at INR 50,000 allocation; do not mislabel it as 0007 | Unidentified “Jetson compatible” listing is not exact-kit evidence | Earlier 0007 observation INR 68,000 cannot be silently replaced with a 0000 price; regional-use caveat stays visible |
| D03 Radar | IWR1843BOOST provides 76–81 GHz 3TX/4RX, onboard processing and accessible processed UART development workflow | LD2450 retained for bench only; not equivalent front vehicle-geometry research evidence | AWR1843BOOST's automotive-chip lineage does not qualify the entire demonstrator. DCA1000/raw-ADC capture is unnecessary for processed target evidence |
| D04 Credible radar comparison | IWR6843ISK is a documented 60–64 GHz research alternative, not an inferior sensor by default. No demonstrated task benefit here warrants changing the selected 76–81 GHz processing/mount baseline | Unspecified “77 GHz sensor” without documented output/profile cannot be integrated responsibly | No numerical superiority or fog immunity inferred from carrier frequency alone |
| D05 RGB | Exact B0200 IMX291 lens/format identity is more useful than unknown webcam branding. Strong low-light product positioning is a test hypothesis | Owned webcam lacks frozen optics/formats; use as reference | IMX327/stereo/depth upgrade lacks a measured benefit for this budget. Manual exposure is preferred but unverified; horizontal-FOV target is not overstated |
| D06 Thermal | Lepton 3.5 with PureThermal 3 is a complete 160 x 120 LWIR acquisition assembly | MLX90640's 32 x 24 class does not meet the requested flagship spatial-detail target | 256/320/640-class thermal requires cost/interface analysis without proof it is needed for this first characterization |
| D07 GNSS | Three identical Waveshare 33000 kits provide two rovers and a local base. Use manufacturer-supplied active antennas | LC29H(AA) is not an RTK replacement. One rover alone cannot demonstrate physical two-vehicle cooperation | ZED-F9P-based boards are credible alternatives, but no observed local requirement establishes a benefit sufficient to fund three pricier assemblies |
| D08 IMU | Adafruit 4754 BNO085 on SPI adds yaw-rate/acceleration and calibrated orientation outputs. Keep INT/RST in interface planning | Random MPU6050 module lacks the selected 9-axis/fusion interface and traceable breakout | BNO086 or industrial INS is not needed without evidence of inadequate BNO085 timing/noise. No inertial positioning through prolonged GNSS loss is promised |
| D09 Wheel feedback | Two 14-bit SPI magnetic angle channels, one measured wheel per side, with geometry-deferred assembly SKU | Motor command alone cannot verify wheel response; a simple single pulse does not establish direction | Replacing all TT motors with premium encoder motors is unjustified before measuring mechanical compatibility |
| D10 Display | Exact Waveshare 11199 7-inch 1024 x 600 HMI | Laptop-only display fails the local driver-interface role | High-resolution/rugged commercial HMI lacks first-demonstrator value |
| D11 Storage | 500 GB NVMe with bounded compressed recording; sizing in budget document | Pi SD card alone is not selected for multi-stream evidence storage | 1 TB adds capacity, not evidence quality. Retention planning supports 500 GB, subject to actual bitrate measurement |
| D12 Network | One TL-WR902AC V3 AP; Jetson Ethernet, Pi/laptop Wi-Fi. Main-node internet not required | Phone hotspot creates an avoidable test-fixture dependency | LTE/LoRa/V2X hardware does not solve a demonstrated local-test problem |
| D13 USB/display accessories | Powered UH720 V5.0; passive DP2HDMI2; UGREEN 60116 data cables | Charge-only cables and unpowered aggregate USB load are unacceptable substitutes | 4K60 active conversion and expensive imported USB cables add no required data capability |
| D14 Alert | Seeed 107020000 buzzer plus existing visual display | Visual-only HMI misses an inexpensive second warning modality | Haptic/beacon/siren array is cosmetic without a validated requirement |
| D15 Drive/control | Retain ESP32/L298N/TT/chassis roles, subject to actual identity/rating checks | Never use unknown rail/current assumptions to save protection cost | Model motion is an assistance-chain demonstration, not a HEMM powertrain replica |
| D16 Power | Separate electronics power, protected branches and independent manual traction interruption | L298N 5 V rail and damaged LM2596 explicitly prohibited | Industrial PLC/contactors are not selected merely to suggest certification; select load-appropriate physical interruption in Prompt 2 |
| D17 Test fixtures | Reserve calibration, mounting and artificial-aerosol test resources | Uncontrolled smoke and unlabelled demo videos cannot establish an operating domain | Commercial meteorological visibility instrument not needed for a clearly limited comparative optical-reference experiment |

Comparison sources: [TI IWR6843ISK](https://www.ti.com/tool/IWR6843ISK), [TI AWR1843BOOST](https://www.ti.com/tool/AWR1843BOOST), [u-blox ZED-F9P](https://www.u-blox.com/en/product/zed-f9p-module), [Waveshare LC29H variant table](https://www.waveshare.com/lc29h-gps-hat.htm). Selected-part primary sources are in document 03. Alternatives are not hidden purchases.

## Changes from earlier records

| Change ID | Earlier record | Current M1 decision | Reason / preservation |
|---|---|---|---|
| M1-01 | Batch A procurement/INR 205,000 ceiling | Technical planning/INR 250,000 additional ceiling | New user instruction; no historical record overwritten |
| M1-02 | GPIO16/17 described as verified in preliminary reply | Under investigation; no final right-channel assignment | Latest prompt explicitly overrides that preliminary certainty |
| M1-03 | India/Taiwan Jetson 0007 and unresolved budget | Exact 0000 technical kit with disclosed regional caveat | Real separate listing, not a fabricated price for 0007 |
| M1-04 | Active DP2HD4K60S, premium USB2AC1M cables | Passive DP2HDMI2, UGREEN 60116 | Manufacturer host support; lower accessory cost for the actual required modes |
| M1-05 | No selected IMU/alert in old Batch-A electronics list | BNO085 SPI and Grove buzzer included | Complementary motion evidence and multimodal warning |
| M1-06 | Wheel SKU prevented mechanical freeze | Freeze technology/performance with dimensioned hub-envelope handoff | Explicit user exception; no fake shaft compatibility |
| M1-07 | Power procurement incomplete | Category freeze plus INR 18,000 allocation | User assigns detailed power schematic/component sizing to Prompt 2 |

Major categories have one decision. Unknown as-built measurements, regional approval and experimental outcomes remain unknown; they are not filled by marketing assumptions.
