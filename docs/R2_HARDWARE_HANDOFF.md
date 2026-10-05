# TARK R2 — website-to-hardware integration handoff

HISTORICAL foundation handoff. Current R3 software boundaries and remaining
physical/protocol gates are in [R3 reasoning](R3_REASONING_REPORT.md),
[vendor formats](R3_VENDOR_FORMATS.md) and [the freeze](TARK_R3_PRESELECTION_FREEZE.md).
The earlier “must implement” rows below record the 3 October milestone.

3 October 2026 · Software-first integration plan · No physical verification claimed

## The important boundary

The website can display normalized observations without knowing vendor packet layouts. This is the correct separation for future integration, but it does **not** mean every newly selected device is already plug-and-play.

The authoritative new hardware architecture is `docs/tark-r2-flagship-redesign/`. It selects a **human-operated instrument cart**, not the old powered acrylic robot. There is no motor driver, automatic steering or brake actuator in that flagship BOM. Keep the existing software's `DISABLED_PHASE_1` invariant; do not repurpose a browser button as a physical safety control.

Selecting a part in a report is not driver verification. Wiring, delivered revision, timing, calibration, operating-domain and mechanical/electrical release gates remain separate.

## What exists and what must still be integrated

| Selected hardware/function | Reusable software boundary | Remaining device-specific work |
|---|---|---|
| Raspberry Pi 5 + Hailo-8 AI HAT+ 26 TOPS | Existing backend/API, normalization, logging and frontend | Install supported Pi runtime; select/compile a supported model, validate input preprocessing/output interpretation, benchmark concurrent inference, capture, recording and HMI. No inference throughput is inferred from TOPS. |
| TI IWR6843ISK | Radar detection/health/perception boundary | Freeze actual EVM revision and approved radar profile/output specification; implement and fixture-test its documented packet/TLV decoder, units, axes, limits, timing and lost-frame handling. The existing **LD2450 decoder is not a TI driver**. |
| Arducam B0200 IMX291 | Existing identity-gated UVC acquisition and media/status boundary | Verify actual UVC formats and selected resolution/frame rate, compression, timestamps, dropped-frame handling and reconnect behavior on the Pi. Hardware is not probed by the demo. |
| Lepton 3.5 + PureThermal 3 | Thermal frame/health display contract | Implement/review USB stream formats and device metadata, frame geometry, shutter/FFC state, calibration and invalid-frame handling. The existing **MLX90640 I2C grid reader is not a Lepton driver**. Do not infer temperature from displayed colours. |
| Three Waveshare LG290P kits | Existing normalized GNSS fix/location/freshness API | Verify output sentences and receiver configuration, base versus rover role, RTCM relay, correction age, coordinate reference and actual quality fields. The existing receiver boundary is not proof of LG290P identity or RTK performance. |
| BNO085 over SPI through measurement MCU | Existing normalized motion/health concepts | Implement the documented BNO085 sensor protocol and MCU timestamp path; validate report types, axes, units, quality/status and recovery. **BNO055 software cannot be relabelled BNO085.** |
| Two AMT102-V measurement wheels | Existing wheel-response calculations and bounded interface concepts | Observation-only counter firmware, exact released pins, resolution/decoding factor, overflow/direction handling, measured circumference and track, slip/disagreement reporting. Wheel response is not ground-truth speed. |
| ESP32-S3-DevKitC-1-N8 measurement MCU A | Existing bounded framing/session/checksum/validation machinery | Review a versioned observation contract and implement IMU/wheel acquisition without motor authority. The existing tested control protocol does not establish a new measurement firmware image or physical USB enumeration. |
| ESP32 node B / peer network | New website participant capability presentation | Implement authenticated/identified timestamped node telemetry and correction transport; validate reconnect, sequence/session changes, stale/reordered messages and bounded queues. A display fixture is not physical peer communication. |
| Fixed base + shared laptop/AP | Fleet/course data presentation and existing local API | Base configuration, correction routing, time/reference management, RF coverage and access controls. Internet-free operation does not mean operation without the local radio network. |
| Seven-inch HDMI touch panel / buzzer | Responsive browser presentation | Physical resolution, brightness, touch targets, daylight/night readability, driver comprehension and audible output integration. No industrial alarm or safety certification is inferred. |

No old GPIO map, supply voltage, protection rating or cable pinout is released by this software handoff. Use the controlled electrical design for the delivered hardware, not a UI label.

## Communication contracts to preserve

1. **Acquisition:** device data enters one owned adapter/worker. Do not open the same serial/camera device independently from the dashboard.
2. **Normalization:** validate types, bounds, units, coordinate frame, device identity, timestamp semantics and source quality before publication.
3. **Health:** disconnected, stale, invalid, degraded and unsupported states are real information. Missing samples are not zeros and never become simulated samples silently.
4. **Local processing:** the core decision pipeline consumes accepted evidence. Browser rendering is not a decision or motor authority.
5. **Publication:** existing REST and WebSocket publish normalized data/decisions; camera media uses a separate stream path. No credentials in WebSocket URLs.
6. **Recording:** preserve observation/source timestamps, host receipt, sequence/session, configuration/calibration revision and original decisions. Retain invalid/fault evidence where bounded and appropriate.
7. **Replay:** historical source provenance stays visible. Replay does not enter live device or actuation paths.

The current control protocol is versioned and includes a session revision; do not create another ad-hoc JSON-over-serial path or silently send new messages to old firmware. Observation-only R2 firmware needs a reviewed compatibility decision, shared vectors and host-side tests before any board is flashed.

## Fleet and location rules

- Vehicle A has the full sensor package. Node B is a **location-only participant**. It has no fabricated radar, camera, body orientation at rest or independent PV-SOE verdict.
- GNSS measures each receiver's own position. Network communication distributes peer observations; GNSS does not discover nearby vehicles.
- Maintain fix quality, correction age, peer message age and clock uncertainty independently.
- Stale peers remain labelled last-known or unavailable; loss of a link is not proof the shared road is clear.
- Do not identify a radar target as node B solely because they appear nearby on a screen.
- Radar local coordinates remain separate from geographic coordinates until a calibrated, timestamp-aligned transform supports placement.
- A position trail is not a surveyed drivable corridor. Guidance requires a reviewed graph, permitted directions/closures and valid road association.
- RTCM correction traffic and peer telemetry have different validation/timing requirements. A functioning dashboard WebSocket proves neither correction delivery nor RTK accuracy.

## Current demonstration scene

`GET /api/v1/flagship` is a **read-only software presentation contract**. In simulation it creates a deterministic, bounded two-participant course. It neither replaces the normalized GNSS service nor injects those coordinates into the decision engine.

Its route, obstacle, coordinates and participant movement are labelled synthetic and not surveyed. Its map cannot be used for real navigation. The core decision and radar simulation remain separately sourced from `/api/v1/status`. A demonstration that displays both is not evidence that the new cooperative conflict algorithm has been implemented or physically validated.

In a non-simulation runtime the fixture does not invent live participants. Real R2 publication needs the genuine adapter/peer integration above. Preserve this separation when replacing fixtures with acquired data.

## Hardware-arrival sequence

1. **Identify unpowered equipment.** Record labels, board revisions, connectors and vendor documentation. Do not select an arbitrary device path based only on enumeration order.
2. **Complete electrical/mechanical review.** Resolve the controlled design's open gates before powering or mounting. Software personnel must not invent fuse values, interfaces or sensor geometry to finish a demo.
3. **Freeze configuration and contracts.** Record device identity, profile/firmware, expected messages, units, bounds, timestamps, calibration version and allowed operating domain.
4. **Use recorded/vendor fixtures first.** Test complete, truncated, corrupt, out-of-order, rebooted, stale and oversized inputs, plus reader shutdown/reconnect. Keep queues and storage bounded.
5. **Commission one approved device at a time.** Use an explicitly selected path and reviewed supply. Capture a bounded raw sample; compare reported behavior with its documentation. Do not enable unrelated adapters.
6. **Validate normalization.** Compare raw records with normalized values and the UI. Confirm that removing the device produces an unavailable state, not a plausible frozen value.
7. **Establish spatial and temporal calibration.** Record sensor extrinsics, antenna lever arm, wheel scaling, clock mappings and uncertainty. Do not equate receipt time with exposure time.
8. **Integrate on the stationary cart.** Measure CPU, memory, USB bandwidth, frame age, drops, processing latency, storage growth and restart recovery under combined load.
9. **Integrate the two-node network.** Verify peer identity, corrections, link loss, duplicate/out-of-order frames, stale positions and node reboot without overclaiming radio coverage or accuracy.
10. **Proceed only through released test gates.** The human operator and mechanical brakes remain responsible for movement. Published EVM capability is not a measured safety envelope.

## Evidence required before changing a maturity label

| Label | Minimum meaning |
|---|---|
| IMPLEMENTED | Identified source module and configuration path exist. |
| SOFTWARE VERIFIED | Named reproducible tests exercised that path with documented fixtures; no hardware claim. |
| HARDWARE PENDING | Software may exist, but the selected physical component/path has not supplied commissioning evidence. |
| PHYSICALLY VERIFIED | Captured evidence for the actual selected device, interface, profile and conditions; not blanket system validation. |
| VALIDATED / safety-ready | Requires a separate defined validation case. Do not assign this to the research platform based on a website or host tests. |

The website work is not authority to flash devices, open serial ports, probe I2C, energize mains, drive motors or alter PV-SOE. It makes the system easier to inspect while retaining the real integration and physical-release work explicitly.
