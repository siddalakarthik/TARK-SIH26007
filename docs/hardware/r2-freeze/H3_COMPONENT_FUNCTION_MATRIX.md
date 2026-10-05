# TARK R2 — H3 functional allocation

Revision A0, 1 October 2026. **NOT FROZEN.** This allocates the assessed design; it does not implement future R2 behavior or establish physical compatibility. Exactly one primary authority class is assigned to each physical BOM row. Passive accessories inherit the supported path's class for bookkeeping only; they gain no decision authority.

All statements below about a physical cutoff remaining available describe the required future failure boundary, **not an existing selected or verified cutoff**. GAP-CUTOFF remains open. Similarly, endpoint expiry and bounded R2 requests require later controlled integration; the table does not assert that R1 drives the current robot.

## Main computation and sensing

| BOM / component | Physical/data input → output | Primary function; secondary function | Later software owner | Primary authority | Failure → lost capability → remaining capability | Dependent capabilities / does not prove |
|---|---|---|---|---|---|---|
| A01 Jetson | Timestamped observations and health → computed evidence, bounded requests, records | Main R2 perception/decision-support owner; local API/HMI host | R2 runtime/core | COMPUTE / DECISION SUPPORT | Compute loss → local high-level functions lost → independent cutoff remains; endpoint expiry must be implemented/tested later | Association, tracking, logging; no certified braking or already-integrated R2 policy |
| A02 IWR1843BOOST | Reflected RF → documented processed measurements | Range/radial-motion evidence; radar characterization | Radar adapter | OBSERVATION ONLY | Radar failure → radar geometry/velocity unavailable → RGB/thermal/GNSS still have their separate evidence | Radar tracks and valid derived TTC; no guaranteed free corridor or object identity |
| A03 B0200 | Visible scene light → timestamped color frames | Semantic/image evidence; degradation assessment | RGB adapter/perception | OBSERVATION ONLY | Camera failure → visual semantics lost → radar ranging and thermal signatures can remain | RGB classification research; no metric range from one uncalibrated image or fog guarantee |
| A04 Lepton core | LWIR radiation → thermal pixel data | Complementary thermal signatures; low-light evidence | Thermal adapter through A05 | OBSERVATION ONLY | Core failure → thermal evidence lost → radar/RGB can remain | Thermal corroboration; no distance, perfect fog vision or clinical temperature measurement |
| A05 PureThermal | Core data → USB thermal stream | Bridge A04 to host; diagnostic acquisition | Thermal adapter | OBSERVATION ONLY | Bridge failure → host loses thermal stream even if core is powered → unrelated channels remain | Complete thermal acquisition; a displayed heatmap alone does not verify radiometry |
| A10 NVMe SSD | Host writes → persistent files | Boot and evidence storage; replay dataset retention | OS/recording service | COMPUTE / DECISION SUPPORT | Storage failure → boot/recording can fail → physical cutoff independent; endpoint must not retain request | Recording/replay support; no guaranteed endurance/runtime/data-loss immunity |
| A11 powered hub | Host USB + external supply → sensor/touch ports | Expand required host connectivity; isolate consumer loads from simple port-count assumptions | OS USB stack | OBSERVATION ONLY | Hub/power loss → attached thermal/GNSS/touch unavailable → directly connected radar/RGB/ESP32 can remain | Shared failure domain explicitly acknowledged; not a safety isolator |
| A14 USB data cables | USB-A host data/power → USB-C peripherals | Link one thermal and three GNSS units; serviceable harness | OS/device adapters | OBSERVATION ONLY | Cable failure → affected channel disconnect/staleness → other channels remain | Correctly typed data paths; no timing synchronization or isolation guarantee |

## Position, communications and HMI

| BOM / component | Physical/data input → output | Primary function; secondary function | Later software owner | Primary authority | Failure → lost capability → remaining capability | Dependent capabilities / does not prove |
|---|---|---|---|---|---|---|
| A06 rover A | Satellite signals + corrections → position and quality | Main vehicle context; trajectory recording | GNSS/location adapter | CONTEXT ONLY | Receiver/correction loss → position unavailable/degraded → local perception remains | Outdoor positioning; no stationary heading or guaranteed absolute centimetres |
| A07 rover B | Independent satellite signals + corrections → second-node position | Actual second physical fleet node; cooperative context | Pi node-B relay | CONTEXT ONLY | Receiver loss → node-B position lost → node A and local perception remain | Independent node evidence; not duplicate map data or second autonomy system |
| A08 base | Satellite observations + configured reference → RTCM corrections | Shared correction source; reference-position record | Base relay on A25 | CONTEXT ONLY | Base failure → RTK convergence/fixed status may be lost on both rovers → standalone fixes may remain, not guaranteed | Differential experiment; self-survey does not validate true base coordinates |
| A26 three kit antennas | Satellite RF → receiver RF inputs | Reception for base and rovers; repeatable reference-plane placement | No executable owner; GNSS acquisition dependent | CONTEXT ONLY | Antenna/cable failure → corresponding positioning lost/degraded → independent local sensors remain | No board-level compatibility until connector/bias/bands verified |
| A15 Pi 3B+ | Rover-B serial data + network corrections → node-B telemetry and serial corrections | Second-node relay only; node health | Node-B service | CONTEXT ONLY | Pi failure → node B disappears → node A/local decision path remains | Reuse without duplicate perception; no safety authority or assumed real-time inference |
| A23 microSD | Pi boot/config/limited logs → usable node-B service | Boot Pi; retain node diagnostics | Pi OS | CONTEXT ONLY | Card failure → Pi/node B unavailable → node A remains | Storage support; not main video recorder or verified card endurance |
| A12 AP | Ethernet/Wi-Fi packets → local network transport | Corrections and fleet/HMI telemetry; incident transfer | Network service, no decision ownership | CONTEXT ONLY | AP failure → remote views and correction distribution lost → onboard compute/local sensors and physical cutoff remain | Local connectivity, not mine-wide V2X or guaranteed RF latency |
| A09 display | Video + touch/power → driver-visible presentation and UI events | Local assistance display; status inspection | Monitoring HMI | MONITORING ONLY | Display failure → local visual assistance lost → computation/cutoff can remain | Readable evidence, not permission to move or motor authority |
| A13 DP-to-HDMI adapter | DP video → HDMI video | Connect display to chosen host; no other role | OS display stack | MONITORING ONLY | Adapter failure → display unavailable → local computation can remain | Connector/protocol conversion, not demonstrated EDID compatibility |
| A25 existing PC | Base serial observations + local network → RTCM forwarding and browser view | Shared stationary base host; control-room monitoring | Base relay and browser, separated processes | CONTEXT ONLY | PC failure → base relay/control-room view lost → onboard sensing/compute remains | No remote motion authority; monitoring is secondary, hence one CONTEXT ONLY classification |

## Robot and retained bench assets

| BOM / component | Physical/data input → output | Primary function; secondary function | Later software owner | Primary authority | Failure → lost capability → remaining capability | Dependent capabilities / does not prove |
|---|---|---|---|---|---|---|
| A16 ESP32-S3 | Later bounded requests and wheel signals → local output state/status | Local supervision; later wheel acquisition | Endpoint firmware | LOCAL SUPERVISION | Endpoint fault → supervision/feedback may be lost → independent physical cutoff must remain available | Board-specific binding still required; not a certified ECU or verified watchdog |
| A18 L298N | Input signals + traction energy → switched motor voltage | Existing TT motor drive; no extra supply role | Endpoint output layer | MOTION OUTPUT | Driver fault → motion unavailable or unintended drive possible → rated independent cutoff required | Working directional test is not thermal/current certification or active braking |
| A19 four TT motors | Switched electrical energy → wheel torque/rotation | Small robot motion; load for feedback trials | Endpoint requests through A18 | MOTION OUTPUT | Motor/mechanical fault → asymmetric/absent wheel response → sensing can still operate separately | No HEMM dynamics, absolute wheel speed or stall-current assumption |
| A20 chassis | Component loads/wheel forces → supported geometry | Physical integration and containment; serviceable sensor reference | No executable owner; mechanical assembly owner | MOTION OUTPUT | Cracking/mount shift → unstable motion and invalid calibration → stop test, inspect hardware | Passive support only, no command authority; payload/stability not verified |
| A21 unidentified traction pack | Stored energy → DC traction supply | Energy source for current robot; no assumed logic-supply role | No executable owner; protection design | MOTION OUTPUT | Supply fault → loss of drive or electrical hazard → no automatic safe-state claim without verified protection | Voltage observation does not prove chemistry, safe charging or capacity |
| A22 SLA bench battery | Stored energy → bench DC energy | Retained bench asset; no active-robot power assumption | Test operator under later approved plan | TEST / CALIBRATION ONLY | Battery failure → bench tests unavailable → R2 architecture not granted battery redundancy | No verified capacity/runtime or regulator compatibility |
| A17 LD2450 | Reflected RF → existing bench radar observations | Compare current prototype evidence with new radar; regression reference | Existing bench tools, separate from flagship primary path | TEST / CALIBRATION ONLY | Bench radar loss → comparison unavailable → flagship A02 path unaffected | Not equivalent to IWR1843 or industrial collision avoidance |
| A24 existing webcam | Scene light → reported Pi video stream | Bench/reference streaming; integration comparison | Existing Pi bench tools | TEST / CALIBRATION ONLY | Webcam failure → comparison stream lost → A03 path unaffected | Reported stream does not identify model/lens or validate perception |

## Unfilled functions are not silently implemented

- Wheel sensing has **no released H2 item**. It would be OBSERVATION ONLY. Do not reuse old GPIO4/5 encoder assignments: U02 reports those pins now drive L298N IN1/IN2. GPIO16/17 are also already assigned to IN3/IN4.
- Physical traction interruption has **no released H2 item**. It must have PHYSICAL POWER INTERRUPTION authority and remain independent of the network/Jetson/browser. The unidentified switch and bare relay do not fulfill it.
- Mobile electronics energy/protection has **no released exact item**. R01 funds its later design but is not a battery or a regulator.

## Reserve accountability

| Reserve | Function funded | H1 links | Authority |
|---|---|---|---|
| R01 | Protected power, cutoff, conversion and mobile supply | 013, 014, 018, 019, 031 | Not a physical component; no authority assigned |
| R02 | Mounts, guards and fabrication | 007, 010, 015, 028, 030 | Not a physical component |
| R03 | Remaining harness/connectors | 027, 028, 031 | Not a physical component |
| R04 | Calibration, wheel pickup provision and measurement aids | 015, 016, 029 | Not a physical component |
| R05 | Controlled low-visibility experiment | 030 | Not a physical component |
| R06 | Repair spares | 028, 031 | Not a physical component |
| R07 | Freight/import uncertainty | 031, 032 | Not a physical component |
| R08 | Integration contingency | 031 | Not a physical component |

The main compute failure-to-expiry behavior is a later R2 requirement, not a hardware-only guarantee. Neither network availability nor a normal UI state grants movement. R1 remains unchanged and zero-output throughout this batch.
