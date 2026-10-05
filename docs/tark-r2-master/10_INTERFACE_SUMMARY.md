# TARK R2 — interface and power-category handoff

Revision M1 • Functional interfaces only. **Not a pin-to-pin wiring instruction.**

## Functional allocation

| Source / component | Link | Owner / sink | Output / responsibility | Failure handling requirement |
|---|---|---|---|---|
| IWR1843BOOST | Onboard XDS110 USB-UART; separate documented 5 V supply | Jetson direct USB-A | Profile/version-tagged processed radar observations | Silence/parse failure invalidates geometry; no fabricated normalized data |
| B0200 RGB | Supplied USB UVC link | Jetson direct USB-A | Frames, timing and format metadata | Missing/frozen/late frames explicitly unavailable |
| ESP32-S3 owned board | Existing reviewed serial/USB boundary; actual board port verification pending | Jetson direct USB-A | Bounded requests and endpoint feedback | Expiry/disconnect/invalid session cannot grant authority; no new protocol defined here |
| UH720 V5.0 | Supplied USB upstream cable | Jetson fourth USB-A port | Powered expansion for low-bandwidth peripherals | Shared hub failure must invalidate each affected source |
| PureThermal 3 + Lepton | USB-C to hub data port via M15 | Jetson | Thermal frame plus validity/FFC/timing data | No last-frame-as-live; distinguish display from radiometric interpretation |
| Rover A LG290P | USB-C to hub data port via M15 | Jetson | Fix/status/observations; correction input | No synthetic fix on loss; preserve receiver state and correction age |
| LCD touch | USB to hub data port | Jetson | Touch events only | Touch/browser has no direct motion authority |
| BNO085 breakout | SPI plus chip select, INT and RST | Jetson 3.3 V logic interface | Inertial/orientation reports, calibration/health | I2C not selected; host SPI/SH-2 support must be integrated later, not claimed working |
| Two magnetic wheel sensors | Shared SPI bus, independent selects, diagnostic validity | ESP32 | Left/right wheel angle, signed response and sample time | Invalid/missing/ambiguous samples remain invalid; not ground speed |
| Grove buzzer | GPIO to assembled module input | ESP32 | Audible local warning pattern | Warning-only load; no traction switching or power authority |
| DP2HDMI2 + LCD | Jetson DP → adapter → HDMI | Driver | Visual HMI | Display failure does not grant motion authority |
| NVMe | M.2 2280 PCIe storage | Jetson | Local bounded evidence/logging | Full/damaged storage reported; recording failure not silently ignored |
| AP TL-WR902AC V3 | Short Ethernet to Jetson; Wi-Fi to peer/laptop | Local research network | RTCM corrections, timestamped peer state, monitoring | No internet requirement; peer expiry and correction loss visible |
| Rover B LG290P | USB-C to Pi via M15 | Owned Pi 3B+ | Physical second-node location and telemetry | Node B is a carried/cart node, not a purchased second AI vehicle |
| Base LG290P | USB-C to laptop via M15 | Fixed local base relay | RTCM correction stream, base status/reference | Base coordinates/reference must be established; base movement invalidates assumed reference |

The AP can travel with the main demonstrator so the short Jetson Ethernet lead does not tether the vehicle. The laptop/base and Pi peer use the local wireless network. Actual RF performance is a test outcome. The AP and hub are not certified outdoor/mine equipment.

Four Jetson host ports are allocated once. Only the hub's seven **data** ports carry sensors; its charging-only ports do not. USB camera bandwidth, topology contention, backfeed, hub inrush and disconnect recovery require bench validation. Four M15 leads serve three GNSS kits and one thermal bridge. Display HDMI/touch, radar USB, ESP32 cable, hub upstream and AP Ethernet leads are included-package inventory or R04 harness provisions, not hidden assumed sensors.

## Positioning and cooperative data path

Fixed base → laptop USB relay → local IP correction distribution → Jetson/Pi serial forwarding → rover A/B receivers. Each rover's fix/quality/time → local vehicle-location contract → local map/control-room observations. Route-graph conflicts use time/quality-qualified peer state, never direct peer motor commands. No public internet correction subscription is required by this architecture.

A base “survey-in” or averaged position is not automatically an accurate absolute mine datum. Establish the relationship between base coordinates, surveyed course, map and antenna lever arms. Preserve fix/float/no-fix and correction age. A single antenna cannot provide reliable standstill heading; IMU/motion history is bounded auxiliary evidence.

## Power categories locked for Prompt 2

| Domain | Category decision | Sizing/release rule |
|---|---|---|
| Traction | Owned pack role retained pending chemistry/protection verification; isolated branch allocation from electronics | Battery/charger identity, peak load and protections must be established before use; voltage reading is not chemistry |
| Electronics energy | New protected LiFePO4 battery category with manufacturer-matched charger, separate from traction | Capacity/current/weight and exact series configuration sized in Prompt 2; no charging procedure specified here |
| Compute | Protected regulated 19 V branch for selected Jetson kit | Validate full input range, startup transient and connector polarity against delivered kit; included bench PSU is not mobile power |
| Hub | Protected regulated 12 V branch | V5.0 documented supply rating is 12 V/3.3 A, not measured draw; converter topology must cover battery range |
| Sensors/Pi/display/AP | Documented regulated 5 V branches, individually protected where required | Radar guide calls for supply capacity above 2.5 A; this is not measured radar current. Pi, display, AP, USB aggregate and cable drop separately budgeted |
| Logic / IMU | 3.3 V signal-level domain; BNO085 breakout powered at matching 3.3 V design selection | No 5 V injection into 3.3 V GPIO; actual breakout/connector limits govern |
| Protection | Battery-side and branch fuses, polarity/short-circuit/thermal/undervoltage protection and strain relief | Ratings follow verified wire/connector/load characteristics; this document assigns none |
| Physical interruption | Independent latching DC traction disconnect, with inhibited restart | Not ESP32 software, unidentified switch or unverified bare relay; stopping/coasting must be measured |

A **100 W aggregate regulated-output sizing envelope** is a conservative Prompt-2 design target, not measured consumption and not a promise every branch can simultaneously use its PSU rating. Sum real loads and startup peaks before selecting converters. Example energy sizing relation: `E_pack >= P_load * runtime_hours / (efficiency * usable_fraction)`; all terms need justified values. Pack mass, safe payload and center of gravity also constrain mobile use. No runtime is promised.

Separate power domains do not imply galvanic isolation or an assumed ground topology. Prompt 2 must define signal returns, bonding, loop control, USB backfeed prevention and noise isolation. L298N 5 V must not feed the compute/controllers. The burnt LM2596 cannot re-enter the design.

## Pin-map and implementation holds

Retain GPIO4→IN1 and GPIO5→IN2 as reported; GPIO16/17 remain unverified. Confirm ESP32 exact board labels/reserved PSRAM/flash pins before assigning wheel SPI, buzzer or right motor signals. No new pins are assigned here. BNO085 SPI modes/INT/RST and Jetson header configuration must follow the documented breakout/host, not guessed Raspberry Pi pin equivalence.

This file does not modify source code, command authority, protocol version, watchdog implementation or current `DISABLED_PHASE_1` behavior. New R2 radar, thermal, IMU, corrections and wheel drivers must be developed and tested in a later authorized software task; purchases alone do not make them interoperable.
