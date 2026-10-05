# 02 — Hardware interface control document

Revision M2-E1. Logical ICD, NOT released pin-to-pin wiring. Every record expands all requested fields; physical unknowns stay explicit. Rail records reference the reviewed sizing method in [04](04_POWER_ARCHITECTURE.md). Current outputs remain zero.

3.3 V logic is not a device supply rating. NOT PUBLISHED means absent from reviewed evidence. USB standard interfaces are not loose TTL UART wires. Maximum voltage is not inferred from nominal. No unknown connector may be connected on this document alone.

## C01 — Jetson to IWR1843BOOST

| Field | Definition |
|---|---|
| CONNECTION_ID | C01 |
| DEVICE_A | Jetson |
| DEVICE_A_PORT_OR_PIN | USB-A U1 |
| SIGNAL_NAME | RADAR_USB |
| SIGNAL_TYPE | Differential USB |
| DIRECTION | Bidirectional; acquisition B to A, control A to B |
| PROTOCOL | USB-UART |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | 5 V VBUS; not a GPIO signal |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Supplied micro-USB data lead |
| CONNECTOR | USB-A / micro-USB |
| DEVICE_B | IWR1843BOOST |
| DEVICE_B_PORT_OR_PIN | XDS110 USB |
| GROUND_REFERENCE | USB cable ground/interface reference; review DC return bonds and backfeed across supplies |
| SHIELDING_REQUIREMENT | Use intact compliant shielded data cable |
| HOT_PLUG_ALLOWED? | USB protocol supports connection; assembled-system hot-plug NOT RELEASED until inrush/backfeed qualification |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Radar geometry lost; invalidate, never clear road |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C02 — Jetson to B0200

| Field | Definition |
|---|---|
| CONNECTION_ID | C02 |
| DEVICE_A | Jetson |
| DEVICE_A_PORT_OR_PIN | USB-A U2 |
| SIGNAL_NAME | RGB_USB |
| SIGNAL_TYPE | Differential USB |
| DIRECTION | Bidirectional; acquisition B to A, control A to B |
| PROTOCOL | USB UVC |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | 5 V VBUS; not a GPIO signal |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Supplied camera lead |
| CONNECTOR | USB-A / supplied camera connector |
| DEVICE_B | B0200 |
| DEVICE_B_PORT_OR_PIN | UVC connector |
| GROUND_REFERENCE | USB cable ground/interface reference; review DC return bonds and backfeed across supplies |
| SHIELDING_REQUIREMENT | Use intact compliant shielded data cable |
| HOT_PLUG_ALLOWED? | USB protocol supports connection; assembled-system hot-plug NOT RELEASED until inrush/backfeed qualification |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Semantics unavailable; reject frozen frames |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C03 — Jetson to UH720 V5

| Field | Definition |
|---|---|
| CONNECTION_ID | C03 |
| DEVICE_A | Jetson |
| DEVICE_A_PORT_OR_PIN | USB-A U4 |
| SIGNAL_NAME | HUB_USB |
| SIGNAL_TYPE | Differential USB |
| DIRECTION | Bidirectional USB transactions between host and downstream hub |
| PROTOCOL | USB 3 host |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA with USB VBUS interface; hub load power from P03; upstream backfeed must be excluded |
| NOMINAL_VOLTAGE | 5 V VBUS; not a GPIO signal |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Supplied upstream lead |
| CONNECTOR | USB-A / actual upstream connector |
| DEVICE_B | UH720 V5 |
| DEVICE_B_PORT_OR_PIN | Upstream port |
| GROUND_REFERENCE | USB cable ground/interface reference; review DC return bonds and backfeed across supplies |
| SHIELDING_REQUIREMENT | Use intact compliant shielded data cable |
| HOT_PLUG_ALLOWED? | USB protocol supports connection; assembled-system hot-plug NOT RELEASED until inrush/backfeed qualification |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Shared downstream loss; invalidate each source |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C04 — UH720 to PURETHERMAL-3

| Field | Definition |
|---|---|
| CONNECTION_ID | C04 |
| DEVICE_A | UH720 |
| DEVICE_A_PORT_OR_PIN | Data D1 |
| SIGNAL_NAME | THERMAL_USB |
| SIGNAL_TYPE | Differential USB |
| DIRECTION | Bidirectional; acquisition B to A, control A to B |
| PROTOCOL | USB UVC/control |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | 5 V VBUS; not a GPIO signal |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | UGREEN 60116 |
| CONNECTOR | USB-A / USB-C |
| DEVICE_B | PURETHERMAL-3 |
| DEVICE_B_PORT_OR_PIN | USB-C |
| GROUND_REFERENCE | USB cable ground/interface reference; review DC return bonds and backfeed across supplies |
| SHIELDING_REQUIREMENT | Use intact compliant shielded data cable |
| HOT_PLUG_ALLOWED? | USB protocol supports connection; assembled-system hot-plug NOT RELEASED until inrush/backfeed qualification |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Thermal acquisition unavailable |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C05 — PURETHERMAL-3 to Lepton 3.5

| Field | Definition |
|---|---|
| CONNECTION_ID | C05 |
| DEVICE_A | PURETHERMAL-3 |
| DEVICE_A_PORT_OR_PIN | Lepton socket |
| SIGNAL_NAME | LEPTON_LOCAL |
| SIGNAL_TYPE | Board-local digital data/control and regulated power |
| DIRECTION | Thermal image data B to A; clocks, configuration and power A to B; control/status exchanges as documented |
| PROTOCOL | VoSPI/control/local power |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | See interface/device specification; no external rail injection |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Board socket; no external loose harness |
| CONNECTOR | Keyed manufacturer socket |
| DEVICE_B | Lepton 3.5 |
| DEVICE_B_PORT_OR_PIN | Mating module contacts |
| GROUND_REFERENCE | PT3/Lepton local return through the designed mating socket |
| SHIELDING_REQUIREMENT | Preserve manufacturer cable/connector shield; no improvised earth changes |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Fit/remove core only with PT3 unpowered; use bridge-managed core sequencing; never inject an external core rail |
| FAILURE_EFFECT | No thermal frames; no invented temperature |
| NOTES | Core receives power/control via PT3 socket only, no direct battery or guessed socket contacts. |

## C06 — UH720 to GNSS-01

| Field | Definition |
|---|---|
| CONNECTION_ID | C06 |
| DEVICE_A | UH720 |
| DEVICE_A_PORT_OR_PIN | Data D2 |
| SIGNAL_NAME | GNSS_A_USB |
| SIGNAL_TYPE | Differential USB |
| DIRECTION | Bidirectional; acquisition B to A, control A to B |
| PROTOCOL | USB-UART NMEA/RTCM documented profile |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | 5 V VBUS; not a GPIO signal |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | UGREEN 60116 |
| CONNECTOR | USB-A / USB-C |
| DEVICE_B | GNSS-01 |
| DEVICE_B_PORT_OR_PIN | USB-C |
| GROUND_REFERENCE | USB cable ground/interface reference; review DC return bonds and backfeed across supplies |
| SHIELDING_REQUIREMENT | Use intact compliant shielded data cable |
| HOT_PLUG_ALLOWED? | USB protocol supports connection; assembled-system hot-plug NOT RELEASED until inrush/backfeed qualification |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Location/corrections degrade |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C07 — Jetson to Owned ESP32-S3

| Field | Definition |
|---|---|
| CONNECTION_ID | C07 |
| DEVICE_A | Jetson |
| DEVICE_A_PORT_OR_PIN | USB-A U3 |
| SIGNAL_NAME | ENDPOINT_USB |
| SIGNAL_TYPE | Differential USB |
| DIRECTION | Bidirectional; acquisition B to A, control A to B |
| PROTOCOL | Reviewed Protocol V2 physical binding |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | 5 V VBUS; not a GPIO signal |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Board-matched data lead |
| CONNECTOR | PHYSICAL PIN CONFIRMATION REQUIRED |
| DEVICE_B | Owned ESP32-S3 |
| DEVICE_B_PORT_OR_PIN | Verified data connector required |
| GROUND_REFERENCE | USB cable ground/interface reference; review DC return bonds and backfeed across supplies |
| SHIELDING_REQUIREMENT | Use intact compliant shielded data cable |
| HOT_PLUG_ALLOWED? | USB protocol supports connection; assembled-system hot-plug NOT RELEASED until inrush/backfeed qualification |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Retire session; output disabled |
| NOTES | No claim native USB/bridge transport is already bound. Strict V2 remains sole current contract. |

## C08 — Jetson to Adafruit 4754

| Field | Definition |
|---|---|
| CONNECTION_ID | C08 |
| DEVICE_A | Jetson |
| DEVICE_A_PORT_OR_PIN | Expansion header SPI/CS/INT/RST |
| SIGNAL_NAME | IMU_SPI |
| SIGNAL_TYPE | Single-ended digital |
| DIRECTION | SCLK/MOSI/CS/RST A to B; MISO/INT B to A; power per P07 |
| PROTOCOL | SH-2 over SPI |
| LOGIC_LEVEL | 3.3 V design; receiver thresholds/carrier verified before release |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | 3.3 V selected VIN and host logic; Adafruit VIN documented 3–5 V, not a GPIO maximum |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Short paired-reference harness |
| CONNECTOR | PHYSICAL PIN CONFIRMATION REQUIRED |
| DEVICE_B | Adafruit 4754 |
| DEVICE_B_PORT_OR_PIN | SCL/SDA/DI/CS/INT/RST/VIN/GND |
| GROUND_REFERENCE | Host local GND; return alongside signals |
| SHIELDING_REQUIREMENT | Short harness with adjacent return, away from motor leads; shield termination reviewed |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Orientation/aiding unavailable |
| NOTES | BNO085 SPI: SCL=SCLK, SDA=MISO, DI=MOSI; CS, INT, RST required; P0/P1 SPI mode per Adafruit. Jetson header numbers NOT assigned. |

## C09 — ESP32-S3 to Left magnetic carrier

| Field | Definition |
|---|---|
| CONNECTION_ID | C09 |
| DEVICE_A | ESP32-S3 |
| DEVICE_A_PORT_OR_PIN | SPI and ENC_LEFT_CS |
| SIGNAL_NAME | ENCODER_LEFT_SPI |
| SIGNAL_TYPE | Single-ended digital |
| DIRECTION | Clock/select/command A to B; angle/status B to A; exact selected carrier protocol required |
| PROTOCOL | Selected carrier SPI profile pending |
| LOGIC_LEVEL | 3.3 V design; receiver thresholds/carrier verified before release |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | 3.3 V logic; carrier supply HOLD if unidentified |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Short local shield/return-aware harness |
| CONNECTOR | PHYSICAL PIN CONFIRMATION REQUIRED |
| DEVICE_B | Left magnetic carrier |
| DEVICE_B_PORT_OR_PIN | SPI pins |
| GROUND_REFERENCE | Host local GND; return alongside signals |
| SHIELDING_REQUIREMENT | Short harness with adjacent return, away from motor leads; shield termination reviewed |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Left wheel response invalid |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C10 — ESP32-S3 to Right magnetic carrier

| Field | Definition |
|---|---|
| CONNECTION_ID | C10 |
| DEVICE_A | ESP32-S3 |
| DEVICE_A_PORT_OR_PIN | SPI and ENC_RIGHT_CS |
| SIGNAL_NAME | ENCODER_RIGHT_SPI |
| SIGNAL_TYPE | Single-ended digital |
| DIRECTION | Clock/select/command A to B; angle/status B to A; exact selected carrier protocol required |
| PROTOCOL | Selected carrier SPI profile pending |
| LOGIC_LEVEL | 3.3 V design; receiver thresholds/carrier verified before release |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | 3.3 V logic; carrier supply HOLD if unidentified |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Short local shield/return-aware harness |
| CONNECTOR | PHYSICAL PIN CONFIRMATION REQUIRED |
| DEVICE_B | Right magnetic carrier |
| DEVICE_B_PORT_OR_PIN | SPI pins |
| GROUND_REFERENCE | Host local GND; return alongside signals |
| SHIELDING_REQUIREMENT | Short harness with adjacent return, away from motor leads; shield termination reviewed |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Right wheel response invalid |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C11 — Jetson to NV3 SNV3S/500G

| Field | Definition |
|---|---|
| CONNECTION_ID | C11 |
| DEVICE_A | Jetson |
| DEVICE_A_PORT_OR_PIN | M.2 Key-M 2280 |
| SIGNAL_NAME | NVME |
| SIGNAL_TYPE | Standard interface |
| DIRECTION | Bidirectional storage commands/completions/data |
| PROTOCOL | PCIe/NVMe |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | See interface/device specification; no external rail injection |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Board slot, no cable |
| CONNECTOR | M.2 Key-M |
| DEVICE_B | NV3 SNV3S/500G |
| DEVICE_B_PORT_OR_PIN | M.2 edge |
| GROUND_REFERENCE | Host M.2 slot ground contacts; no external power or return injection |
| SHIELDING_REQUIREMENT | Preserve manufacturer cable/connector shield; no improvised earth changes |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Fit/remove only with host fully unpowered; OS unmount/shutdown before power removal |
| FAILURE_EFFECT | Recording unavailable/full/corrupt visible |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C12 — Jetson to DP2HDMI2

| Field | Definition |
|---|---|
| CONNECTION_ID | C12 |
| DEVICE_A | Jetson |
| DEVICE_A_PORT_OR_PIN | DisplayPort |
| SIGNAL_NAME | HMI_DP |
| SIGNAL_TYPE | Standard interface |
| DIRECTION | Video A to B; display identification/status via documented auxiliary interface |
| PROTOCOL | DisplayPort |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DISPLAY DATA and standard interface auxiliary supply only; not LCD load power |
| NOMINAL_VOLTAGE | See interface/device specification; no external rail injection |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Adapter |
| CONNECTOR | DP |
| DEVICE_B | DP2HDMI2 |
| DEVICE_B_PORT_OR_PIN | DP male |
| GROUND_REFERENCE | DisplayPort connector reference/shield per supplied interface |
| SHIELDING_REQUIREMENT | Preserve manufacturer cable/connector shield; no improvised earth changes |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Visual HMI unavailable |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C13 — DP2HDMI2 to Waveshare 11199

| Field | Definition |
|---|---|
| CONNECTION_ID | C13 |
| DEVICE_A | DP2HDMI2 |
| DEVICE_A_PORT_OR_PIN | HDMI female |
| SIGNAL_NAME | HMI_HDMI |
| SIGNAL_TYPE | Standard interface |
| DIRECTION | Video A to B; display identification/status via documented display interface |
| PROTOCOL | HDMI |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DISPLAY DATA and standard interface auxiliary supply only; LCD power per P11 |
| NOMINAL_VOLTAGE | See interface/device specification; no external rail injection |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Qualified short HDMI lead from R04/inventory |
| CONNECTOR | HDMI |
| DEVICE_B | Waveshare 11199 |
| DEVICE_B_PORT_OR_PIN | HDMI input |
| GROUND_REFERENCE | HDMI reference/shield per supplied interface |
| SHIELDING_REQUIREMENT | Preserve manufacturer cable/connector shield; no improvised earth changes |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Visual HMI unavailable |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C14 — UH720 to Waveshare 11199

| Field | Definition |
|---|---|
| CONNECTION_ID | C14 |
| DEVICE_A | UH720 |
| DEVICE_A_PORT_OR_PIN | Data D3 |
| SIGNAL_NAME | HMI_TOUCH |
| SIGNAL_TYPE | Differential USB |
| DIRECTION | Bidirectional; acquisition B to A, control A to B |
| PROTOCOL | USB HID |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | 5 V VBUS; not a GPIO signal |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Delivered USB lead |
| CONNECTOR | Actual panel connector verify |
| DEVICE_B | Waveshare 11199 |
| DEVICE_B_PORT_OR_PIN | Touch/power USB per revision |
| GROUND_REFERENCE | USB cable ground/interface reference; review DC return bonds and backfeed across supplies |
| SHIELDING_REQUIREMENT | Use intact compliant shielded data cable |
| HOT_PLUG_ALLOWED? | USB protocol supports connection; assembled-system hot-plug NOT RELEASED until inrush/backfeed qualification |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Touch/power lost; no motion authority |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C15 — Jetson to TL-WR902AC V3

| Field | Definition |
|---|---|
| CONNECTION_ID | C15 |
| DEVICE_A | Jetson |
| DEVICE_A_PORT_OR_PIN | Ethernet |
| SIGNAL_NAME | NET_MAIN |
| SIGNAL_TYPE | Differential Ethernet |
| DIRECTION | Bidirectional IP data |
| PROTOCOL | Ethernet IP |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA ONLY; no PoE or AP power through this link is specified |
| NOMINAL_VOLTAGE | Interface-defined differential signalling, not a DC supply rail |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Short Cat5e or better qualified lead |
| CONNECTOR | RJ45 |
| DEVICE_B | TL-WR902AC V3 |
| DEVICE_B_PORT_OR_PIN | LAN |
| GROUND_REFERENCE | Ethernet interface magnetics; no intentional DC power-return bond through signal pairs |
| SHIELDING_REQUIREMENT | Preserve manufacturer cable/connector shield; no improvised earth changes |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Peer/correction/control-room loss, local sensing continues |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C16 — TL-WR902AC V3 to Pi 3B+

| Field | Definition |
|---|---|
| CONNECTION_ID | C16 |
| DEVICE_A | TL-WR902AC V3 |
| DEVICE_A_PORT_OR_PIN | Wi-Fi AP |
| SIGNAL_NAME | NET_PEER |
| SIGNAL_TYPE | Wireless RF data |
| DIRECTION | Bidirectional IP telemetry/corrections |
| PROTOCOL | Local Wi-Fi IP |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA ONLY; nodes powered independently |
| NOMINAL_VOLTAGE | NOT APPLICABLE: no conductive inter-node supply |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT APPLICABLE to wireless path; node supply limits are separate |
| CABLE | Not applicable: radio |
| CONNECTOR | Not applicable |
| DEVICE_B | Pi 3B+ |
| DEVICE_B_PORT_OR_PIN | Wi-Fi |
| GROUND_REFERENCE | No wired shared return through this radio path |
| SHIELDING_REQUIREMENT | No cable shield; preserve antennas and antenna clearance |
| HOT_PLUG_ALLOWED? | NOT APPLICABLE; association/reconnect subject to identity/session gates |
| POWER_SEQUENCE_REQUIREMENT | Each node powers from its qualified source; link reconnection cannot restore authority without fresh evidence |
| FAILURE_EFFECT | Peer/correction loss |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C17 — TL-WR902AC V3 to Owned laptop

| Field | Definition |
|---|---|
| CONNECTION_ID | C17 |
| DEVICE_A | TL-WR902AC V3 |
| DEVICE_A_PORT_OR_PIN | Wi-Fi AP |
| SIGNAL_NAME | NET_BASE |
| SIGNAL_TYPE | Wireless RF data |
| DIRECTION | Bidirectional IP fleet/correction/control-room data |
| PROTOCOL | Local Wi-Fi IP |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA ONLY; nodes powered independently |
| NOMINAL_VOLTAGE | NOT APPLICABLE: no conductive inter-node supply |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT APPLICABLE to wireless path; node supply limits are separate |
| CABLE | Not applicable: radio |
| CONNECTOR | Not applicable |
| DEVICE_B | Owned laptop |
| DEVICE_B_PORT_OR_PIN | Wi-Fi |
| GROUND_REFERENCE | No wired shared return through this radio path |
| SHIELDING_REQUIREMENT | No cable shield; preserve antennas and antenna clearance |
| HOT_PLUG_ALLOWED? | NOT APPLICABLE; association/reconnect subject to identity/session gates |
| POWER_SEQUENCE_REQUIREMENT | Each node powers from its qualified source; link reconnection cannot restore authority without fresh evidence |
| FAILURE_EFFECT | Correction/monitoring loss |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C18 — Pi 3B+ to GNSS-02

| Field | Definition |
|---|---|
| CONNECTION_ID | C18 |
| DEVICE_A | Pi 3B+ |
| DEVICE_A_PORT_OR_PIN | USB host |
| SIGNAL_NAME | GNSS_B_USB |
| SIGNAL_TYPE | Differential USB |
| DIRECTION | Bidirectional; acquisition B to A, control A to B |
| PROTOCOL | USB-UART NMEA/RTCM |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | 5 V VBUS; not a GPIO signal |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | UGREEN 60116 |
| CONNECTOR | USB-A / USB-C |
| DEVICE_B | GNSS-02 |
| DEVICE_B_PORT_OR_PIN | USB-C |
| GROUND_REFERENCE | USB cable ground/interface reference; review DC return bonds and backfeed across supplies |
| SHIELDING_REQUIREMENT | Use intact compliant shielded data cable |
| HOT_PLUG_ALLOWED? | USB protocol supports connection; assembled-system hot-plug NOT RELEASED until inrush/backfeed qualification |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Peer location unavailable |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C19 — Owned laptop to GNSS-03

| Field | Definition |
|---|---|
| CONNECTION_ID | C19 |
| DEVICE_A | Owned laptop |
| DEVICE_A_PORT_OR_PIN | USB host |
| SIGNAL_NAME | GNSS_BASE_USB |
| SIGNAL_TYPE | Differential USB |
| DIRECTION | Bidirectional; acquisition B to A, control A to B |
| PROTOCOL | USB-UART base/RTCM |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | 5 V VBUS; not a GPIO signal |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | UGREEN 60116 |
| CONNECTOR | USB-A / USB-C |
| DEVICE_B | GNSS-03 |
| DEVICE_B_PORT_OR_PIN | USB-C |
| GROUND_REFERENCE | USB cable ground/interface reference; review DC return bonds and backfeed across supplies |
| SHIELDING_REQUIREMENT | Use intact compliant shielded data cable |
| HOT_PLUG_ALLOWED? | USB protocol supports connection; assembled-system hot-plug NOT RELEASED until inrush/backfeed qualification |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Corrections cease; stale reference visible |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C20 — ESP32-S3 to L298N module

| Field | Definition |
|---|---|
| CONNECTION_ID | C20 |
| DEVICE_A | ESP32-S3 |
| DEVICE_A_PORT_OR_PIN | MOTOR_L_A/B; MOTOR_R_A/B logical outputs |
| SIGNAL_NAME | MOTOR_LOGIC |
| SIGNAL_TYPE | Single-ended digital |
| DIRECTION | Logic requests A to B; no physical motor feedback through IN1–IN4 |
| PROTOCOL | Digital direction; future enables gated |
| LOGIC_LEVEL | 3.3 V design; receiver thresholds/carrier verified before release |
| POWER_OR_DATA | CONTROL DATA ONLY; motor and module supplies are separate |
| NOMINAL_VOLTAGE | 3.3 V host logic design; exact module input compatibility must be verified |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Separated signal/return harness |
| CONNECTOR | Actual module terminals verify |
| DEVICE_B | L298N module |
| DEVICE_B_PORT_OR_PIN | IN1/IN2/IN3/IN4 |
| GROUND_REFERENCE | ESP GND to verified L298N logic reference; no motor current through this lead |
| SHIELDING_REQUIREMENT | Short harness with adjacent return, away from motor leads; shield termination reviewed |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Traction isolated; qualified rails first, owner opens once after identity check; stop owner before planned disconnect |
| FAILURE_EFFECT | Motor request invalid; physical cutoff independent |
| NOTES | GPIO4/5 reported only. GPIO16/17 NOT FROZEN. ENA/ENB installed jumpers are not validated PWM or reset inhibition. |

## C21 — ESP32-S3 to Grove 107020000

| Field | Definition |
|---|---|
| CONNECTION_ID | C21 |
| DEVICE_A | ESP32-S3 |
| DEVICE_A_PORT_OR_PIN | BUZZER logical pin |
| SIGNAL_NAME | BUZZER |
| SIGNAL_TYPE | Single-ended digital |
| DIRECTION | Control SIG A to B; supply/return from reviewed endpoint rail, not GPIO load power |
| PROTOCOL | Digital module input |
| LOGIC_LEVEL | 3.3 V design; receiver thresholds/carrier verified before release |
| POWER_OR_DATA | DATA plus assigned local power |
| NOMINAL_VOLTAGE | 3.3 V logic; carrier supply HOLD if unidentified |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Grove breakout lead |
| CONNECTOR | Grove orientation verify |
| DEVICE_B | Grove 107020000 |
| DEVICE_B_PORT_OR_PIN | SIG/VCC/GND |
| GROUND_REFERENCE | Grove GND to ESP local logic return |
| SHIELDING_REQUIREMENT | Preserve manufacturer cable/connector shield; no improvised earth changes |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Assemble unpowered; qualified module rail and reference before active signal; do not back-power through SIG |
| FAILURE_EFFECT | Audible alert lost, visual warning remains |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C22 — GNSS-01 to Bundled active antenna

| Field | Definition |
|---|---|
| CONNECTION_ID | C22 |
| DEVICE_A | GNSS-01 |
| DEVICE_A_PORT_OR_PIN | RF connector |
| SIGNAL_NAME | GNSS_A_RF |
| SIGNAL_TYPE | RF |
| DIRECTION | GNSS RF B to A; documented active-antenna DC bias A to B |
| PROTOCOL | GNSS RF with documented bias |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA / RF; RF bias only documented board |
| NOMINAL_VOLTAGE | See interface/device specification; no external rail injection |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Bundled RF lead |
| CONNECTOR | Delivered mating RF verify |
| DEVICE_B | Bundled active antenna |
| DEVICE_B_PORT_OR_PIN | A mating RF |
| GROUND_REFERENCE | Coax shield/receiver reference; no extra bias |
| SHIELDING_REQUIREMENT | Preserve supplied coax/shield |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Connect documented antenna/coax with receiver unpowered; no external bias injection |
| FAILURE_EFFECT | No/poor fix; quality not fabricated |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C23 — GNSS-02 to Bundled active antenna

| Field | Definition |
|---|---|
| CONNECTION_ID | C23 |
| DEVICE_A | GNSS-02 |
| DEVICE_A_PORT_OR_PIN | RF connector |
| SIGNAL_NAME | GNSS_B_RF |
| SIGNAL_TYPE | RF |
| DIRECTION | GNSS RF B to A; documented active-antenna DC bias A to B |
| PROTOCOL | GNSS RF with documented bias |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA / RF; RF bias only documented board |
| NOMINAL_VOLTAGE | See interface/device specification; no external rail injection |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Bundled RF lead |
| CONNECTOR | Delivered mating RF verify |
| DEVICE_B | Bundled active antenna |
| DEVICE_B_PORT_OR_PIN | B mating RF |
| GROUND_REFERENCE | Coax shield/receiver reference; no extra bias |
| SHIELDING_REQUIREMENT | Preserve supplied coax/shield |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Connect documented antenna/coax with receiver unpowered; no external bias injection |
| FAILURE_EFFECT | No/poor fix; quality not fabricated |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C24 — GNSS-03 to Bundled active antenna

| Field | Definition |
|---|---|
| CONNECTION_ID | C24 |
| DEVICE_A | GNSS-03 |
| DEVICE_A_PORT_OR_PIN | RF connector |
| SIGNAL_NAME | GNSS_BASE_RF |
| SIGNAL_TYPE | RF |
| DIRECTION | GNSS RF B to A; documented active-antenna DC bias A to B |
| PROTOCOL | GNSS RF with documented bias |
| LOGIC_LEVEL | Interface-defined; not GPIO TTL |
| POWER_OR_DATA | DATA / RF; RF bias only documented board |
| NOMINAL_VOLTAGE | See interface/device specification; no external rail injection |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Bundled RF lead |
| CONNECTOR | Delivered mating RF verify |
| DEVICE_B | Bundled active antenna |
| DEVICE_B_PORT_OR_PIN | BASE mating RF |
| GROUND_REFERENCE | Coax shield/receiver reference; no extra bias |
| SHIELDING_REQUIREMENT | Preserve supplied coax/shield |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Connect documented antenna/coax with receiver unpowered; no external bias injection |
| FAILURE_EFFECT | No/poor fix; quality not fabricated |
| NOTES | Frozen role; actual identity, operating mode, cable and configuration captured at commissioning. |

## C25 — L298N to TT LEFT_FRONT

| Field | Definition |
|---|---|
| CONNECTION_ID | C25 |
| DEVICE_A | L298N |
| DEVICE_A_PORT_OR_PIN | Left output pair |
| SIGNAL_NAME | MOTOR_LEFT_FRONT |
| SIGNAL_TYPE | Switched power |
| DIRECTION | Switched motor energy A to B; inductive/freewheel energy returns through the reviewed driver circuit |
| PROTOCOL | Switched DC |
| LOGIC_LEVEL | NOT APPLICABLE: motor power, not logic |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | Actual traction range HOLD |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Load-rated paired motor lead |
| CONNECTOR | Rated crimp/terminal HOLD |
| DEVICE_B | TT LEFT_FRONT |
| DEVICE_B_PORT_OR_PIN | Motor terminals |
| GROUND_REFERENCE | N-R2-TRACTION- via H-bridge; neither motor terminal assumed ground |
| SHIELDING_REQUIREMENT | Route paired motor leads away from logic/RF; suppression and shield termination require actual driver review |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Connect only unpowered; traction cutoff open; verify fail-disabled controls and load rating before separately released motion |
| FAILURE_EFFECT | Loss/mismatch; simultaneous paired load qualification required |
| NOTES | Existing paired-wheel connection must be traced; no pin polarity or motor direction is inferred. |

## C26 — L298N to TT LEFT_REAR

| Field | Definition |
|---|---|
| CONNECTION_ID | C26 |
| DEVICE_A | L298N |
| DEVICE_A_PORT_OR_PIN | Left output pair |
| SIGNAL_NAME | MOTOR_LEFT_REAR |
| SIGNAL_TYPE | Switched power |
| DIRECTION | Switched motor energy A to B; inductive/freewheel energy returns through the reviewed driver circuit |
| PROTOCOL | Switched DC |
| LOGIC_LEVEL | NOT APPLICABLE: motor power, not logic |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | Actual traction range HOLD |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Load-rated paired motor lead |
| CONNECTOR | Rated crimp/terminal HOLD |
| DEVICE_B | TT LEFT_REAR |
| DEVICE_B_PORT_OR_PIN | Motor terminals |
| GROUND_REFERENCE | N-R2-TRACTION- via H-bridge; neither motor terminal assumed ground |
| SHIELDING_REQUIREMENT | Route paired motor leads away from logic/RF; suppression and shield termination require actual driver review |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Connect only unpowered; traction cutoff open; verify fail-disabled controls and load rating before separately released motion |
| FAILURE_EFFECT | Loss/mismatch; simultaneous paired load qualification required |
| NOTES | Existing paired-wheel connection must be traced; no pin polarity or motor direction is inferred. |

## C27 — L298N to TT RIGHT_FRONT

| Field | Definition |
|---|---|
| CONNECTION_ID | C27 |
| DEVICE_A | L298N |
| DEVICE_A_PORT_OR_PIN | Right output pair |
| SIGNAL_NAME | MOTOR_RIGHT_FRONT |
| SIGNAL_TYPE | Switched power |
| DIRECTION | Switched motor energy A to B; inductive/freewheel energy returns through the reviewed driver circuit |
| PROTOCOL | Switched DC |
| LOGIC_LEVEL | NOT APPLICABLE: motor power, not logic |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | Actual traction range HOLD |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Load-rated paired motor lead |
| CONNECTOR | Rated crimp/terminal HOLD |
| DEVICE_B | TT RIGHT_FRONT |
| DEVICE_B_PORT_OR_PIN | Motor terminals |
| GROUND_REFERENCE | N-R2-TRACTION- via H-bridge; neither motor terminal assumed ground |
| SHIELDING_REQUIREMENT | Route paired motor leads away from logic/RF; suppression and shield termination require actual driver review |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Connect only unpowered; traction cutoff open; verify fail-disabled controls and load rating before separately released motion |
| FAILURE_EFFECT | Loss/mismatch; simultaneous paired load qualification required |
| NOTES | Existing paired-wheel connection must be traced; no pin polarity or motor direction is inferred. |

## C28 — L298N to TT RIGHT_REAR

| Field | Definition |
|---|---|
| CONNECTION_ID | C28 |
| DEVICE_A | L298N |
| DEVICE_A_PORT_OR_PIN | Right output pair |
| SIGNAL_NAME | MOTOR_RIGHT_REAR |
| SIGNAL_TYPE | Switched power |
| DIRECTION | Switched motor energy A to B; inductive/freewheel energy returns through the reviewed driver circuit |
| PROTOCOL | Switched DC |
| LOGIC_LEVEL | NOT APPLICABLE: motor power, not logic |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | Actual traction range HOLD |
| MAXIMUM_DOCUMENTED_VOLTAGE | NOT PUBLISHED in this connection record; verify delivered interface electrical limits before wiring |
| CABLE | Load-rated paired motor lead |
| CONNECTOR | Rated crimp/terminal HOLD |
| DEVICE_B | TT RIGHT_REAR |
| DEVICE_B_PORT_OR_PIN | Motor terminals |
| GROUND_REFERENCE | N-R2-TRACTION- via H-bridge; neither motor terminal assumed ground |
| SHIELDING_REQUIREMENT | Route paired motor leads away from logic/RF; suppression and shield termination require actual driver review |
| HOT_PLUG_ALLOWED? | NO powered mating in commissioning plan |
| POWER_SEQUENCE_REQUIREMENT | Connect only unpowered; traction cutoff open; verify fail-disabled controls and load rating before separately released motion |
| FAILURE_EFFECT | Loss/mismatch; simultaneous paired load qualification required |
| NOTES | Existing paired-wheel connection must be traced; no pin polarity or motor direction is inferred. |

## P01 — N-R2-ELECTRONICS+

| Field | Definition |
|---|---|
| CONNECTION_ID | P01 |
| DEVICE_A | Electronics protected source |
| DEVICE_A_PORT_OR_PIN | Qualified source output |
| SIGNAL_NAME | N-R2-ELECTRONICS+ |
| SIGNAL_TYPE | DC POWER |
| DIRECTION | A to B |
| PROTOCOL | DC, no data |
| LOGIC_LEVEL | Not a GPIO signal |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | Series/range HOLD |
| MAXIMUM_DOCUMENTED_VOLTAGE | HOLD: delivered load/source range; nominal is not maximum |
| CABLE | Ampacity/drop/inrush sized per 04 |
| CONNECTOR | Exact rated connector/polarity HOLD |
| DEVICE_B | Distribution |
| DEVICE_B_PORT_OR_PIN | Actual input label verify |
| GROUND_REFERENCE | N-R2-E-RETURN |
| SHIELDING_REQUIREMENT | Motor/logic separation; shield not load return |
| HOT_PLUG_ALLOWED? | NO powered mating |
| POWER_SEQUENCE_REQUIREMENT | Unpowered checks; current-limited branch qualification; traction isolated |
| FAILURE_EFFECT | Branch loss/short/undervoltage; Distribution unavailable, no extra authority |
| NOTES | F-E rating HOLD; reverse polarity/short/UV/thermal review; no L298N 5 V or damaged LM2596 |

## P02 — N-R2-C19+

| Field | Definition |
|---|---|
| CONNECTION_ID | P02 |
| DEVICE_A | 19 V converter |
| DEVICE_A_PORT_OR_PIN | Qualified source output |
| SIGNAL_NAME | N-R2-C19+ |
| SIGNAL_TYPE | DC POWER |
| DIRECTION | A to B |
| PROTOCOL | DC, no data |
| LOGIC_LEVEL | Not a GPIO signal |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | 19 V target |
| MAXIMUM_DOCUMENTED_VOLTAGE | HOLD: delivered load/source range; nominal is not maximum |
| CABLE | Ampacity/drop/inrush sized per 04 |
| CONNECTOR | Exact rated connector/polarity HOLD |
| DEVICE_B | Jetson DC input |
| DEVICE_B_PORT_OR_PIN | Actual input label verify |
| GROUND_REFERENCE | Converter OUT- verified |
| SHIELDING_REQUIREMENT | Motor/logic separation; shield not load return |
| HOT_PLUG_ALLOWED? | NO powered mating |
| POWER_SEQUENCE_REQUIREMENT | Unpowered checks; current-limited branch qualification; traction isolated |
| FAILURE_EFFECT | Branch loss/short/undervoltage; Jetson DC input unavailable, no extra authority |
| NOTES | F-C19 rating HOLD; reverse polarity/short/UV/thermal review; no L298N 5 V or damaged LM2596 |

## P03 — N-R2-H12+

| Field | Definition |
|---|---|
| CONNECTION_ID | P03 |
| DEVICE_A | 12 V converter |
| DEVICE_A_PORT_OR_PIN | Qualified source output |
| SIGNAL_NAME | N-R2-H12+ |
| SIGNAL_TYPE | DC POWER |
| DIRECTION | A to B |
| PROTOCOL | DC, no data |
| LOGIC_LEVEL | Not a GPIO signal |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | 12 V |
| MAXIMUM_DOCUMENTED_VOLTAGE | HOLD: delivered load/source range; nominal is not maximum |
| CABLE | Ampacity/drop/inrush sized per 04 |
| CONNECTOR | Exact rated connector/polarity HOLD |
| DEVICE_B | UH720 DC input |
| DEVICE_B_PORT_OR_PIN | Actual input label verify |
| GROUND_REFERENCE | Converter OUT- verified |
| SHIELDING_REQUIREMENT | Motor/logic separation; shield not load return |
| HOT_PLUG_ALLOWED? | NO powered mating |
| POWER_SEQUENCE_REQUIREMENT | Unpowered checks; current-limited branch qualification; traction isolated |
| FAILURE_EFFECT | Branch loss/short/undervoltage; UH720 DC input unavailable, no extra authority |
| NOTES | F-H12 rating HOLD; reverse polarity/short/UV/thermal review; no L298N 5 V or damaged LM2596 |

## P04 — N-R2-S5+

| Field | Definition |
|---|---|
| CONNECTION_ID | P04 |
| DEVICE_A | 5 V radar branch |
| DEVICE_A_PORT_OR_PIN | Qualified source output |
| SIGNAL_NAME | N-R2-S5+ |
| SIGNAL_TYPE | DC POWER |
| DIRECTION | A to B |
| PROTOCOL | DC, no data |
| LOGIC_LEVEL | Not a GPIO signal |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | 5 V |
| MAXIMUM_DOCUMENTED_VOLTAGE | HOLD: delivered load/source range; nominal is not maximum |
| CABLE | Ampacity/drop/inrush sized per 04 |
| CONNECTOR | Exact rated connector/polarity HOLD |
| DEVICE_B | IWR1843BOOST barrel |
| DEVICE_B_PORT_OR_PIN | Actual input label verify |
| GROUND_REFERENCE | Converter OUT-/USB reference |
| SHIELDING_REQUIREMENT | Motor/logic separation; shield not load return |
| HOT_PLUG_ALLOWED? | NO powered mating |
| POWER_SEQUENCE_REQUIREMENT | Unpowered checks; current-limited branch qualification; traction isolated |
| FAILURE_EFFECT | Branch loss/short/undervoltage; IWR1843BOOST barrel unavailable, no extra authority |
| NOTES | F-R5 rating HOLD; reverse polarity/short/UV/thermal review; no L298N 5 V or damaged LM2596 |

## P05 — N-R2-N5+

| Field | Definition |
|---|---|
| CONNECTION_ID | P05 |
| DEVICE_A | 5 V network branch |
| DEVICE_A_PORT_OR_PIN | Qualified source output |
| SIGNAL_NAME | N-R2-N5+ |
| SIGNAL_TYPE | DC POWER |
| DIRECTION | A to B |
| PROTOCOL | DC, no data |
| LOGIC_LEVEL | Not a GPIO signal |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | 5 V |
| MAXIMUM_DOCUMENTED_VOLTAGE | HOLD: delivered load/source range; nominal is not maximum |
| CABLE | Ampacity/drop/inrush sized per 04 |
| CONNECTOR | Exact rated connector/polarity HOLD |
| DEVICE_B | AP power input |
| DEVICE_B_PORT_OR_PIN | Actual input label verify |
| GROUND_REFERENCE | Converter OUT- verified |
| SHIELDING_REQUIREMENT | Motor/logic separation; shield not load return |
| HOT_PLUG_ALLOWED? | NO powered mating |
| POWER_SEQUENCE_REQUIREMENT | Unpowered checks; current-limited branch qualification; traction isolated |
| FAILURE_EFFECT | Branch loss/short/undervoltage; AP power input unavailable, no extra authority |
| NOTES | F-N5 rating HOLD; reverse polarity/short/UV/thermal review; no L298N 5 V or damaged LM2596 |

## P06 — N-R2-P5+

| Field | Definition |
|---|---|
| CONNECTION_ID | P06 |
| DEVICE_A | Peer protected supply |
| DEVICE_A_PORT_OR_PIN | Qualified source output |
| SIGNAL_NAME | N-R2-P5+ |
| SIGNAL_TYPE | DC POWER |
| DIRECTION | A to B |
| PROTOCOL | DC, no data |
| LOGIC_LEVEL | Not a GPIO signal |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | 5 V |
| MAXIMUM_DOCUMENTED_VOLTAGE | HOLD: delivered load/source range; nominal is not maximum |
| CABLE | Ampacity/drop/inrush sized per 04 |
| CONNECTOR | Exact rated connector/polarity HOLD |
| DEVICE_B | Pi power input |
| DEVICE_B_PORT_OR_PIN | Actual input label verify |
| GROUND_REFERENCE | Peer local return |
| SHIELDING_REQUIREMENT | Motor/logic separation; shield not load return |
| HOT_PLUG_ALLOWED? | NO powered mating |
| POWER_SEQUENCE_REQUIREMENT | Unpowered checks; current-limited branch qualification; traction isolated |
| FAILURE_EFFECT | Branch loss/short/undervoltage; Pi power input unavailable, no extra authority |
| NOTES | F-P5 rating HOLD; reverse polarity/short/UV/thermal review; no L298N 5 V or damaged LM2596 |

## P07 — N-R2-J3V3

| Field | Definition |
|---|---|
| CONNECTION_ID | P07 |
| DEVICE_A | Jetson qualified header rail |
| DEVICE_A_PORT_OR_PIN | Qualified source output |
| SIGNAL_NAME | N-R2-J3V3 |
| SIGNAL_TYPE | DC POWER |
| DIRECTION | A to B |
| PROTOCOL | DC, no data |
| LOGIC_LEVEL | Not a GPIO signal |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | 3.3 V |
| MAXIMUM_DOCUMENTED_VOLTAGE | HOLD: delivered load/source range; nominal is not maximum |
| CABLE | Ampacity/drop/inrush sized per 04 |
| CONNECTOR | Exact rated connector/polarity HOLD |
| DEVICE_B | BNO085 VIN |
| DEVICE_B_PORT_OR_PIN | Actual input label verify |
| GROUND_REFERENCE | Jetson GND |
| SHIELDING_REQUIREMENT | Motor/logic separation; shield not load return |
| HOT_PLUG_ALLOWED? | NO powered mating |
| POWER_SEQUENCE_REQUIREMENT | Unpowered checks; current-limited branch qualification; traction isolated |
| FAILURE_EFFECT | Branch loss/short/undervoltage; BNO085 VIN unavailable, no extra authority |
| NOTES | Host/detail review rating HOLD; reverse polarity/short/UV/thermal review; no L298N 5 V or damaged LM2596 |

## P08 — N-R2-ESP3V3

| Field | Definition |
|---|---|
| CONNECTION_ID | P08 |
| DEVICE_A | Endpoint qualified local rail |
| DEVICE_A_PORT_OR_PIN | Qualified source output |
| SIGNAL_NAME | N-R2-ESP3V3 |
| SIGNAL_TYPE | DC POWER |
| DIRECTION | A to B |
| PROTOCOL | DC, no data |
| LOGIC_LEVEL | Not a GPIO signal |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | 3.3 V logic; carrier supply verify |
| MAXIMUM_DOCUMENTED_VOLTAGE | HOLD: delivered load/source range; nominal is not maximum |
| CABLE | Ampacity/drop/inrush sized per 04 |
| CONNECTOR | Exact rated connector/polarity HOLD |
| DEVICE_B | Wheel carriers and Grove module |
| DEVICE_B_PORT_OR_PIN | Actual input label verify |
| GROUND_REFERENCE | ESP GND |
| SHIELDING_REQUIREMENT | Motor/logic separation; shield not load return |
| HOT_PLUG_ALLOWED? | NO powered mating |
| POWER_SEQUENCE_REQUIREMENT | Unpowered checks; current-limited branch qualification; traction isolated |
| FAILURE_EFFECT | Branch loss/short/undervoltage; Wheel carriers and Grove module unavailable, no extra authority |
| NOTES | Board/detail review rating HOLD; reverse polarity/short/UV/thermal review; no L298N 5 V or damaged LM2596 |

## P09 — N-R2-T-PROTECTED+

| Field | Definition |
|---|---|
| CONNECTION_ID | P09 |
| DEVICE_A | Qualified traction pack through source-proximate F-T |
| DEVICE_A_PORT_OR_PIN | F-T protected output |
| SIGNAL_NAME | N-R2-T-PROTECTED+ |
| SIGNAL_TYPE | DC POWER |
| DIRECTION | A to B |
| PROTOCOL | DC, no data |
| LOGIC_LEVEL | Not a GPIO signal |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | Pack range HOLD |
| MAXIMUM_DOCUMENTED_VOLTAGE | HOLD: delivered load/source range; nominal is not maximum |
| CABLE | Ampacity/drop/inrush sized per 04 |
| CONNECTOR | Exact rated connector/polarity HOLD |
| DEVICE_B | Rated manual cutoff |
| DEVICE_B_PORT_OR_PIN | Cutoff input; contact/polarity labels verify |
| GROUND_REFERENCE | N-R2-TRACTION- |
| SHIELDING_REQUIREMENT | Motor/logic separation; shield not load return |
| HOT_PLUG_ALLOWED? | NO powered mating |
| POWER_SEQUENCE_REQUIREMENT | Unpowered checks; current-limited branch qualification; traction isolated |
| FAILURE_EFFECT | Fuse/source loss removes motor energy availability; no increased authority |
| NOTES | N-R2-T-PROTECTED+ starts at F-T output, not the unfused pack terminal. Unfused lead must be shortest practical protected routing; F-T and pack remain rating HOLD. |

## P10 — N-R2-TRACTION+

| Field | Definition |
|---|---|
| CONNECTION_ID | P10 |
| DEVICE_A | Rated manual cutoff output |
| DEVICE_A_PORT_OR_PIN | Qualified source output |
| SIGNAL_NAME | N-R2-TRACTION+ |
| SIGNAL_TYPE | DC POWER |
| DIRECTION | A to B |
| PROTOCOL | DC, no data |
| LOGIC_LEVEL | Not a GPIO signal |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | Pack range HOLD |
| MAXIMUM_DOCUMENTED_VOLTAGE | HOLD: delivered load/source range; nominal is not maximum |
| CABLE | Ampacity/drop/inrush sized per 04 |
| CONNECTOR | Exact rated connector/polarity HOLD |
| DEVICE_B | L298N motor supply |
| DEVICE_B_PORT_OR_PIN | Actual input label verify |
| GROUND_REFERENCE | N-R2-TRACTION- |
| SHIELDING_REQUIREMENT | Motor/logic separation; shield not load return |
| HOT_PLUG_ALLOWED? | NO powered mating |
| POWER_SEQUENCE_REQUIREMENT | Unpowered checks; current-limited branch qualification; traction isolated |
| FAILURE_EFFECT | Branch loss/short/undervoltage; L298N motor supply unavailable, no extra authority |
| NOTES | F-T upstream rating HOLD; reverse polarity/short/UV/thermal review; no L298N 5 V or damaged LM2596 |

## P11 — N-R2-HMI5+

| Field | Definition |
|---|---|
| CONNECTION_ID | P11 |
| DEVICE_A | Hub D3 or reviewed single HMI feed |
| DEVICE_A_PORT_OR_PIN | Qualified source output |
| SIGNAL_NAME | N-R2-HMI5+ |
| SIGNAL_TYPE | DC POWER |
| DIRECTION | A to B |
| PROTOCOL | DC, no data |
| LOGIC_LEVEL | Not a GPIO signal |
| POWER_OR_DATA | POWER |
| NOMINAL_VOLTAGE | 5 V |
| MAXIMUM_DOCUMENTED_VOLTAGE | HOLD: delivered load/source range; nominal is not maximum |
| CABLE | Ampacity/drop/inrush sized per 04 |
| CONNECTOR | Exact rated connector/polarity HOLD |
| DEVICE_B | LCD/touch |
| DEVICE_B_PORT_OR_PIN | Actual input label verify |
| GROUND_REFERENCE | USB/branch return; no dual feed |
| SHIELDING_REQUIREMENT | Motor/logic separation; shield not load return |
| HOT_PLUG_ALLOWED? | NO powered mating |
| POWER_SEQUENCE_REQUIREMENT | Unpowered checks; current-limited branch qualification; traction isolated |
| FAILURE_EFFECT | Branch loss/short/undervoltage; LCD/touch unavailable, no extra authority |
| NOTES | Hub/detail review rating HOLD; reverse polarity/short/UV/thermal review; no L298N 5 V or damaged LM2596 |

## Connector release and sources

USB-powered RGB, ESP, thermal and GNSS are accounted through their host/hub links, not additional parallel supplies. SSD is slot powered; RF antennas use their board bias only. LCD HMI feed is one verified source. Battery charging connections remain manufacturer-matched pack/charger interfaces, not a homemade charger design.

References: [M1 interfaces](../tark-r2-master/10_INTERFACE_SUMMARY.md), [Adafruit pin names](https://learn.adafruit.com/adafruit-9-dof-orientation-imu-fusion-breakout-bno085/pinouts), [TI EVM](https://www.ti.com/tool/IWR1843BOOST), [GPIO holds](03_ESP32_GPIO_RESERVATION.md). A final released harness adds connector drawing, pin numbers, cable length and rating evidence per row; placeholders cannot be used as construction instructions.
