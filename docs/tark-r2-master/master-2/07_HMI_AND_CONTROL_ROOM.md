# Master-2 — driver HMI and control-room platform

## 1. Platform and authority

Keep the existing single TARK React/TypeScript application, MapLibre map and FastAPI observation backend. This package specifies R2 presentation requirements; it does not create another frontend or change application code. Serve the compiled frontend and local API from one origin when deployed. Maps and route guidance must have an offline/local-data path; external basemap/geocoding/routing failure does not stop the local decision runtime.

One WebSocket subscription owner per application shell distributes bounded state to views; do not create a sensor reader per tab or rebuild MapLibre on each update. Existing endpoints and `status`/`location_update` event names are documented in 02. New fields need explicit versioned projections and integration tests, not UI-only calculations of TTC or permitted speed.

Control-room and browser permissions remain monitoring-only for motion. Selecting a route/destination can request a reviewed mission plan, never motor output or permission to exceed a local constraint. Acknowledging an alarm records acknowledgement only; it does not clear the cause, reset physical interruption or resume movement.

## 2. Driver view: glanceable before detailed

```text
TARK | source: REAL / SIMULATION / REPLAY | time/connection age
STATE + symbol       REQUIRED ACTION             PRIMARY REASON
current speed*       permitted speed**            TTC / status
next manoeuvre       distance reference           destination
MAP: vehicle heading/uncertainty + route/hazard context
GNSS quality | front evidence | endpoint status | active warning

* identify ground estimate versus wheel response; unavailable is not zero
** permitted speed remains 0 in DISABLED_PHASE_1; no hypothetical cap as approved speed
```

Use text, icon/shape, position and colour together. NORMAL must not be restyled as guaranteed SAFE. Give STOP/UNKNOWN and unavailable evidence high visual priority. Do not make the operator interpret technical covariance matrices while driving; provide a concise uncertainty message and supervisor drill-down.

Buzzer patterns correspond to reviewed warning priorities and are rate-limited to avoid chatter. Startup/module communication is not a successful audibility test. Visual indication remains if the buzzer is unavailable; no camera/thermal live label without fresh frames.

## 3. Supervisor and sensor views

Show selected track evidence, range, relative-motion validity, TTC status, active envelope constraint, stopping-model status, sensor timestamps, calibration, disagreement and route relevance. Preserve numeric units and nulls. A plotted point must link to the observation/track it represents.

| Panel | Required content | Misrepresentation to prevent |
|---|---|---|
| Radar | Local metric top view, axes/origin, tracks/uncertainty/age | Radar x/y shown as geographic coordinates or guaranteed geographic hazards |
| RGB | Actual frame/reference, source, age, model/exposure/quality state | Frozen frame labelled LIVE; synthetic imagery labelled real |
| Thermal | Grid/frame, scale/unit meaning, validity/FFC and age | Palette intensity described as calibrated temperature or range |
| IMU | Attitude/rates, frame/calibration, magnetic health | Uncalibrated yaw called true compass heading |
| Wheels/endpoint | Left/right response validity, age, applied-output status, session/ACK meaning | ACK equals motion; wheel response equals ground speed; current V2 implies wheel telemetry exists |
| GNSS/location | Receiver fix, correction age, reference/map, fused estimate separately | RTK label equals assured lane accuracy; phone location equals vehicle |
| Diagnostics | Runtime/queue/resource health, versions/config/calibration IDs | Process alive equals sensor ONLINE or physically verified |

## 4. Map / navigation presentation

Keep geographic vehicle position separate from browser-device location and the radar local view. A global radar overlay requires a valid pose, lever arm, frame transform and time alignment; otherwise show targets only locally. Do not draw a precise global target marker from uncertain heading.

Distinguish route line from travelled breadcrumb and uncertain prediction. Show accuracy/uncertainty with its provenance; never create a circle radius from a fabricated number. Display graph/map revision, next manoeuvre, closure/hazard validity and selected destination. The India overview is labelled when no vehicle location exists.

Local offline tiles/data must be lawfully available/cached under the provider's terms. A proprietary online map key does not grant arbitrary tile redistribution. If no basemap exists offline, retain the local course graph, reference grid and qualified vehicle/peer positions with an explicit basemap-unavailable label. No additional network subscription is assumed in the frozen hardware budget.

## 5. Fleet / control-room view

One unified role-aware application shows the actual instrumented nodes. Vehicle cards include state, last observation age, fix quality, route/map revision, restrictions, fault reasons and version. Node B is labelled a cooperative research node, not a fully equipped dumper.

Show event counts and durations only from real recorded intervals with defined start/end rules. No invented fleet, near-miss, cycle-time or production metric. A threshold encounter is a conflict event until independently classified; it is not automatically a real near miss or prevented accident.

Highlight stale/offline vehicles, map mismatches, lost correction service and uncertain conflict intervals. Selection opens the evidence behind the warning. A monitoring outage must be visible locally; it cannot cause the vehicle to assume higher authority.

## 6. Events, evidence and replay

Event detail needs original observation IDs, source/calibration/config/software/map versions, source and receive times, transition reason, constraints, requested versus accepted versus applied output, and missing-evidence flags. Index media by bounded references instead of embedding raw frame arrays in status snapshots.

Preserve R1's isolated recording/replay semantics. R2 replay must additionally capture the ordered multi-sensor/peer/localization inputs and initial state needed for its new algorithms. Until those checkpoints and comparisons are implemented, do not call replay of old radar-only input a full R2 verification.

Always distinguish ORIGINAL RECORDING, REPLAY COMPUTATION and LIVE. Display MATCH/MISMATCH/NOT COMPARED only over the explicitly compared fields and record range. A corrupt/incompatible/incomplete recording produces an error or qualified partial view, not a blanket MATCH. Replay can never submit a motion request.

## 7. UX and performance acceptance

Test 320, 375, 430, 768, 1024, 1440 and 1920 px widths. State/action/reason remain readable without horizontal overflow, and map height remains nonzero. Test keyboard access, contrast, long reason codes, empty/stale/error views, slow rendering and disconnect/reconnect. Confirm one map instance and one shell WebSocket owner, bounded histories and paginated/virtualized event views as needed.

For the 7-inch display, test actual viewing distance/glare rather than asserting a pixel count guarantees cab readability. For projector demonstrations, use a presentation layout emphasizing state, reason, map and provenance while retaining all safety limitations. All UX and performance statements here are requirements, not completed test results.
