# Master-2 — failure handling, security and recovery

## 1. Governing rule

No failure, missing evidence, reset or recovery may silently increase motion authority. Current Phase-1 authority is permanently zero. The following describes proposed R2 capability handling; it does not establish that new board-level protections or algorithms have already been implemented.

Separate **capability lost**, **operator presentation**, **local supervisory response** and **physical effect**. A displayed STOP is not proof power was interrupted; an electrical disconnect is not proof a moving vehicle has stopped.

## 2. Failure matrix

| ID | Fault / detection evidence | Capability effect | Required response / recovery criterion |
|---|---|---|---|
| F01 | Radar silence, malformed/profile-mismatched frames, stale data | Primary selected geometry unreliable | Invalidate affected tracks/coverage; UNKNOWN or stronger applicable stop condition; recover only after qualified fresh profile-matched evidence |
| F02 | Valid radar report with no detections | No current detected target; coverage still needs qualification | Do not substitute missing report or declare free space to manufacturer range |
| F03 | Camera unplug/frozen frames/low contrast | Semantic context reduced or absent | Show source age and lost function; radar evidence can remain but not inherit semantics |
| F04 | Thermal FFC, frozen/invalid frame, poor contrast | Thermal corroboration unavailable | Mark gap/validity; no interpolated evidence pretending independence |
| F05 | RGB/radar/thermal disagree or association ambiguous | Object identity/geometry uncertain | Retain competing hypotheses; do not average disagreement into higher confidence |
| F06 | GNSS no fix/float/jump/multipath or stale correction | Global navigation/cooperative location degrades | Preserve reported quality; bounded prediction only; no fake FIX or confident wrong-road assignment |
| F07 | Base reference wrong/moved, correction mismatch | Shared localization error risk | Invalidate reference-dependent claims; require reference/configuration check, not only a fresh packet |
| F08 | IMU calibration loss, magnetic disturbance, rate/axis mismatch | Orientation/prediction uncertainty grows | Reject affected channel; do not use magnetometer as true heading; bounded reinitialization |
| F09 | Wheel angle invalid/stale/wrap ambiguous or L/R mismatch | Wheel response unreliable | Mark invalid, bound prediction; no substitution of requested wheel command as measured feedback |
| F10 | Wheel slip versus GNSS/inertial disagreement | Wheel-to-ground mapping invalid | Retain disagreement; no asserted ground speed/odometry accuracy |
| F11 | Peer loss, old/future timestamp, duplicate session/sequence | Cooperative zone information incomplete | Degraded/unknown cooperative coverage; never “junction clear” from silence |
| F12 | AP/internet/control-room failure | Corrections/peer/monitoring may fail; local channels remain separate | Local acquisition/runtime continues where possible; affected capabilities degrade independently |
| F13 | Wrong map/reference revision, closed edge or ambiguous matching | Route instruction unreliable | Suppress confident manoeuvre; show conflict/uncertainty; no remote override of local limit |
| F14 | Host overload, unbounded-delay risk or reader worker failure | Freshness/timing guarantees lost | Shed noncritical UI/media, expose drops and invalidate delayed evidence; bounded restart, no stale NORMAL |
| F15 | Hub disconnect/power fault | Multiple shared peripherals fail together | Detect individual losses plus common cause; no claim of sensor independence against shared power |
| F16 | ESP32 link/ACK/session failure or stale feedback | Endpoint acceptance unknown | Retire pending session/correlation; outputs remain disabled; heartbeat does not extend an old command |
| F17 | MCU reboot, stale boot identity, scheduler/watchdog failure | Supervision not established | No authority until reviewed fresh identity and independent periodic expiry handling; actual hardware binding still pending |
| F18 | Driver reset pins/ENA-ENB jumper behavior | Potential output ambiguity in a future powered model | Physical traction remains disconnected until passive-safe behavior is reviewed and tested; software zero-after-boot is insufficient |
| F19 | Battery sag/overcurrent/regulator fault | Partial reset/data loss/energy hazard | Protective power behavior, explicit health and safe restart; never bypass protection to finish a demonstration |
| F20 | Physical traction disconnect opened | Traction energy removed if wiring qualifies; coasting possible | Latch event/state as observable; reset requires new deliberate authorization, not automatic motion |
| F21 | Disk full/corrupt or writer queue overflow | Evidence incomplete | Mark recording loss/full status, stop claiming replay completeness; controlled retention policy cannot silently erase retained incidents |
| F22 | Browser stale/disconnected | Operator/control-room observation stale | Prominent stale overlay/age; no browser authority; last-known values not labelled current |
| F23 | Replay incompatible/corrupt/missing records | Comparison unsupported | Explicit error/partial status; no live contamination or blanket MATCH |
| F24 | False/malicious peer, map or observation input | Data trust compromised | Authenticate/validate/bound, reject/revoke, log; CRC alone is not authentication |

Detection criteria requiring future thresholds must be derived from characterized rates/delays and stored in versioned configuration. Do not invent “hardware verified” from worker liveness, ACK or a manufacturer string.

## 3. Recovery lifecycle

For a recoverable reader failure: isolate failed source → close/bound pending I/O → clear partial parsing state while preserving diagnostic counters → bounded retry with backoff → re-identify device/profile → re-establish clock/calibration validity → fresh evidence qualification. Recovery must not reuse pre-fault sample age or automatically lower a stricter latched condition.

Disconnect/reboot invalidates protocol session and queued requests. A fresh handshake is required but alone is not ONLINE feedback. Physical USB, boot-identity and watchdog behavior remain board-integration tasks under the existing V2 contract. No invented ESP-IDF USB code is supplied in this design.

Clock rollback or unknown source time mapping invalidates time-sensitive evidence. UI reconnection obtains a current server snapshot instead of replaying old browser actions. Configuration/map/calibration changes create a new evidence context and must not silently reinterpret existing recordings.

## 4. Security boundaries

Treat AP access, peer identity, browser access and local endpoint authority as distinct controls. Use unique configured credentials and authenticated application channels appropriate to deployment; no secrets in source, images, URLs or logs. Design peer admission/revocation and freshness/replay protection explicitly. WPA access alone is not authenticated vehicle state.

The existing Pi↔ESP32 V2 CRC detects corruption and sessions defend defined replay cases; they do not authenticate a hostile peer. Do not promote that link to an industrial security claim. Physical port access and approved host identity are separate controls.

Viewer/operator/supervisor/engineering roles can inspect appropriate data. Engineering configuration, calibration/map/model changes require a controlled offline/versioned release workflow; no public dashboard slider for braking constants, authority caps or protocol checks. Alarm acknowledgement is not a safety override.

Apply size/type/range limits before expensive parsing. Bound camera/media downloads, WebSocket queues, event pages, peer count, routes and replay records. Reject unexpected endpoints/commands; avoid arbitrary filesystem paths, shell invocation or untrusted URLs from vehicle payloads. Log attempted malformed requests without retaining secret tokens.

Record only needed experimental imagery and identifiers. Use consent/permission for people/site recordings, minimize faces/plates, define retention and access, and redact exports where appropriate. No public upload is part of this task.

## 5. No false redundancy or certification

The three perception channels share compute, mounting/environment and sometimes power/transport. Two GNSS rovers share corrections and can share a wrong reference. A software watchdog is not the same as a verified independent hardware watchdog. A consumer IMU, ESP32 or manual disconnect does not confer a safety integrity level on the complete system.

Hazard severity, exposure and required risk reduction need an actual operational hazard analysis with qualified stakeholders. This matrix deliberately does not invent numerical RPN/SIL/PL or mine-certification status.
