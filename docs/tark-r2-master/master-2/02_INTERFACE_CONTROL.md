# Master-2 — interface control design

## 1. Hardware interface allocation

The M1 models and quantities remain authoritative. Labels below are logical allocations, not discovered device paths or final board-header numbers.

| Link | Source → destination | Data/electrical boundary | Design rule |
|---|---|---|---|
| IF01 | IWR1843BOOST → Jetson USB host 1 | XDS110 USB-UART: configuration and processed output channels distinguished | Bind board identity/port role and documented firmware/profile; no guessed TI packet variant |
| IF02 | B0200 → Jetson USB host 2 | UVC compressed/raw modes as enumerated | Verify exact pixel format, timestamp source and exposure controls |
| IF03 | ESP32 → Jetson USB host 3 | Existing bounded serial transport and **Protocol V2** | Actual board USB/serial path unresolved; no COM selection/probe here |
| IF04 | UH720 → Jetson USB host 4 | Powered USB upstream | Seven data ports, separate charge-only ports; topology/backfeed review |
| IF05 | Lepton/PT3 → hub data 1 | USB-C UVC/radiometric acquisition | Core and bridge jointly identified; display palette is not temperature data |
| IF06 | Rover A → hub data 2 | USB-UART, receiver messages and RTCM input | One serial owner multiplexes supported receiver input/output; not competing readers |
| IF07 | Display touch → hub data 3 | USB touch | Monitoring interaction only |
| IF08 | BNO085 → Jetson expansion interface | SPI SCK/MOSI/MISO/CS plus INT/RST | Matching 3.3 V logic; SH-2 message validation; actual header pins assigned only from carrier documentation |
| IF09 | Left/right magnetic angle carriers → ESP32 | Common SPI clock/data, separate chip-selects | Exact carrier, connector and supply depend on measured assembly; 14-bit technology unchanged |
| IF10 | ESP32 → L298N | Four logical direction inputs; two enable functions | See signal reservation table; existing jumpers do not establish fail-disabled behavior |
| IF11 | ESP32 → Grove buzzer | GPIO signal into documented assembled module | Alert-only; no GPIO directly driving an unbuffered load |
| IF12 | Jetson → DP2HDMI2 → display | DP to HDMI video | No USB-C display assumption; validate EDID |
| IF13 | Jetson → NVMe | M.2 2280 PCIe | Boot/install and thermal/recording performance characterized later |
| IF14 | Jetson ↔ TL-WR902AC | Short Ethernet; AP travels with main node | Base laptop and Pi B communicate on local Wi-Fi |
| IF15 | Rover B ↔ Pi B | One of four frozen USB-A/C data cables | Physical peer location; no invented course/velocity when invalid |
| IF16 | Base ↔ laptop | One of four frozen USB-A/C data cables | Base coordinates/config/status logged; correction relay isolated from motion |

Four M15 leads cover three GNSS receivers plus the thermal bridge. Other required leads remain in included-package checks/M1 harness allocation. No fifth premium receiver or sensor is introduced.

## 2. Logical signal reservations — NOT a wiring table

| Signal | Function | Physical assignment status |
|---|---|---|
| MOTOR_IN1 | L298N IN1 | GPIO4, user-reported preliminary wiring; board inspection pending |
| MOTOR_IN2 | L298N IN2 | GPIO5, user-reported preliminary wiring; board inspection pending |
| MOTOR_IN3 | L298N IN3 | **UNASSIGNED. GPIO16 is under investigation, not approved** |
| MOTOR_IN4 | L298N IN4 | **UNASSIGNED. GPIO17 is under investigation, not approved** |
| MOTOR_ENABLE_L / MOTOR_ENABLE_R | Driver output-enable/inhibit functions | Logical reservations only; current ENA/ENB jumpers reported installed |
| WHEEL_SPI_SCK / MOSI / MISO | Two magnetic-angle channels | Unassigned pending exact board/PSRAM/flash and carrier review |
| WHEEL_CS_L / WHEEL_CS_R | Distinct wheel selections | Unassigned; never share an active chip select |
| ALERT_BUZZER | Local audible warning | Unassigned |
| IMU_SPI_* / IMU_CS / IMU_INT / IMU_RST | BNO085 host interface | Jetson-side logical labels; not ESP32 assignments |
| TRACTION_DISCONNECT | Independent manual energy interruption | Physical power-path function, not an ESP32 GPIO |

Before pin assignment inspect the exact PCB, accessible header labels, boot straps, USB/debug use and memory reservations. ESP32-S3 variant memory wiring can reserve pins; a module name alone is insufficient. [Espressif GPIO guidance](https://docs.espressif.com/projects/esp-idf/en/v6.0/esp32s3/api-reference/peripherals/gpio.html)

Current jumpers hold enables active. A future fail-disabled model interface must have a reviewed passive-safe output/enable design across reset/brownout/disconnection; software writing zero after boot cannot prove that. No jumper or GPIO is changed by M2.

## 3. Proposed observation envelope

Use one normalized observation boundary per device; retain raw diagnostic capture separately. The following are **logical R2 requirements**, not silently added fields in current REST or V2 wire messages.

| Field group | Required meaning |
|---|---|
| Identity | Source/vehicle ID, model, firmware/profile, driver revision, boot/session epoch |
| Provenance | REAL / SIMULATION / REPLAY / TEST_FIXTURE, acquisition path and physical-verification record separately |
| Timing | Device sample time if available, host receive monotonic time, clock domain, estimated offset/uncertainty and sample-age upper bound |
| Geometry/units | Explicit frame ID, SI units, calibration ID and transform revision |
| Validity | Device validity, bounds/finite checks, sequence, complete/partial/empty/no-report distinction, fault reason |
| Uncertainty | Covariance or bounded error with units and basis; null when unestablished, not a made-up precision |
| Payload | Radar observations; RGB reference; thermal grid reference; GNSS fix/quality; inertial report; wheel response |
| Integrity | Schema/version and capture fingerprint; a hash identifies bytes, not truthful physical provenance or authentication |

Reject NaN/infinity, impossible ranges, wrong units, duplicate/out-of-order records and unjustified future timestamps. Record rejection counters. A valid empty radar report is distinct from no report, but **neither proves the entire road is clear**. Preserve source sample time; API polling and WebSocket publication must not freshen it.

## 4. Time and coordinate contract

Use host monotonic time for local age/deadline logic. A timestamp from another computer is not comparable without a clock relationship. Retain receiver UTC separately; GNSS UTC is not automatically the camera exposure clock. USB arrival is receive time, not exposure time. No shared hardware trigger/PPS distribution is claimed in this budget.

For a sensor with known mapping, `age_upper = local_now - mapped_sample_time + timestamp_uncertainty`. If the mapping is absent, use receive time plus a characterized worst-case transport/acquisition delay; if that bound is unknown, the observation cannot support a timing-critical positive claim. Bound future/rollback cases and reset the mapping on device reboot.

The proposed canonical body frame is x-forward, y-left, z-up, metres/radians. GNSS geographical coordinates retain datum/reference; map projection is local ENU with an explicit origin/version. Each existing adapter's actual axis/sign convention must be verified and transformed; do not relabel legacy x/y fields in place. Screen pixel coordinates and radar local coordinates are not latitude/longitude.

## 5. Existing Pi/Jetson ↔ ESP32 protocol is not reopened

The existing [Protocol V2](../../ESP32_PROTOCOL_V2.md) remains the sole current wire authority: bounded COBS, CRC32C, canonical CBOR, session/configuration match, sequence/correlation and receiver-local expiry. V1 remains rejected. No second encoder/decoder, baud assumption, board USB stack or new watchdog implementation is created here.

ACK means acceptance of a disabled-phase command, not motor motion. STATUS is not a new ACK. Heartbeat cannot renew an expired motion request. Host and firmware monotonic epochs are not equated. CRC/session checks are not cryptographic peer authentication. Current outputs remain `DISABLED_PHASE_1` and zero.

**Real integration gap:** V2 STATUS has only its approved fields and does not transport magnetic-angle samples. A future R2 wheel-response extension must be explicitly reviewed/versioned with host, firmware and shared vectors together, through the same transport/service. Reserve the logical record `WHEEL_RESPONSE` (left/right angle, validity, counts/wrap status, sample time/domain and sequence) for that review; assign no wire message number here. Do not stuff it into unknown V2 keys or pretend wheel data exists today. Motion enabling would require a separate approved phase/authority change; this handoff authorizes neither.

## 6. Application projections

Current source defines `/api/v1/status`, `/api/v1/vehicle-location`, `/api/v1/sensors`, `/api/v1/imu`, `/api/v1/thermal`, camera metadata/stream, events, recordings/replay and `/api/v1/ws`. The WebSocket publishes `status` and `location_update`; keep these observational. The browser must not be made an acquisition owner.

R2 additions need explicit versioned projection tests, not frontend-only invented values or overloading legacy sensor meanings. Full video/thermal arrays should use bounded media delivery/storage references, not inflate every status message. Existing replay schemas cannot be called multi-sensor deterministic replay until extended input/checkpoint/compatibility coverage exists.

Primary interface sources: [NVIDIA carrier guide](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html), [TI EVM](https://www.ti.com/tool/IWR1843BOOST), [BNO085 pinouts](https://learn.adafruit.com/adafruit-9-dof-orientation-imu-fusion-breakout-bno085/pinouts), and M1 document 03. Product pages establish capabilities, not successful TARK interoperability.
