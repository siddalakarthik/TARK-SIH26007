# 24 — Software and storage architecture

DESIGN, not production code. Extend actual backend/app, backend/tests, frontend/src, firmware/esp32, shared, simulation, config and scripts conventions; do not create a second application.

## Service boundaries

| Module | Inputs → outputs | Allocation / dependencies |
|---|---|---|
| Sensor adapters | Device bytes/frames → normalized envelopes + diagnostics | One worker per device owner; blocking acquisition thread/process |
| Time manager | Native/host/UTC mappings → bounded age | Library + sampled sync monitor; no clock restamping |
| Health manager | Time/validation/counters → per-task usability | Local decision library; independent of browser |
| Radar | Qualified points/profile → tracks | Bounded CPU worker/library |
| RGB | Qualified frames → quality/boxes/classes | Isolated GPU worker process with bounded latest-frame IPC |
| Thermal | Qualified frames/FFC → regions | Acquisition/processing worker, independent health |
| Tracking/fusion | Time/frame-qualified observations → persistent hypotheses | Local libraries; preserve disagreement |
| Motion/localization | GNSS/IMU/wheels → motion/pose uncertainty | Local estimator library; recorded state |
| Map matching/routing | Pose + reviewed graph/destination → edge/route/guidance | Match in local runtime, route as nonblocking task |
| Fleet context | Authenticated peer messages → qualified peer intervals | Async network service; never hardware owner |
| Risk/envelope/state | Tracks/coverage/motion/context → reasons/capabilities | Single local decision owner; bounded tick |
| Endpoint | Approved request → same protocol/transport → correlated feedback | Existing serialized service plus reviewed future binding |
| Recorder | Ordered evidence/decisions → chunks/catalog | Bounded asynchronous writer, fault visible |
| Replay | Immutable session → isolated computation/comparison | Separate worker, no live transports |
| API/WebSocket | Latest snapshots/events → role projections | Existing FastAPI async tasks; cannot advance local ticks |
| HMI/control room | Projections → presentation | Existing React shell; one WebSocket/map owner |
| Analytics | Recorded sessions → scoped metrics | Offline/bounded job; not safety-loop dependency |
| Config/log/security | Signed versioned settings, audit/auth → validated context | Shared validated libraries and access boundaries |

Camera/GPU process crash invalidates that source; it cannot silently stop expiry or create healthy frames. Restart uses backoff and fresh source epoch; recovery checks precede reuse. Avoid process-per-small-function overhead: pure algorithms are libraries under one deterministic runtime owner. Expensive acquisition/media jobs are isolated where blocking/crashes justify it.

## Resource and backpressure policy

Latest-frame queues replace superseded frames with loss counters; ordered decision-input queues never silently overwrite required records. Overflow sets explicit incomplete-evidence flags. Every queue, track count, peer count, payload and recording byte limit is configured/versioned. Bounded network sends and disk writes cannot delay endpoint expiry. Overload reduces optional video/UI rates first; if required deadlines still fail, withdraw capability.

Configuration selection distinguishes simulation, replay and explicitly enabled real adapters. No auto-simulation injection into a real source on failure. Real acquisition requires identity/configuration gates. Credentials are external, not committed or embedded in a recording.

## Data model

| Metadata entity | Keys / meaning |
|---|---|
| vehicles/hardware_versions | Stable ID, node role, actual identity and maturity |
| software_versions/configurations | Hash/version, approved parameters and rollout |
| calibrations | Hardware/mount/version, parameters/uncertainty/validity |
| maps/routes/restrictions/trips | Datum/revision, route edges, destination and actual trip times |
| observations/tracks | Source/boot/sequence/time, normalized input and derived IDs |
| health_states/reason_codes/events | Ordered cause/state history and taxonomy version |
| incidents/recordings/chunks | Trigger/window, completeness, byte/hash references |
| commands/endpoint_feedback | Sequence/session/config, acceptance separate from physical response |
| audit_actions | Actor/role/action/result/config/map revision |

Use SQLite metadata initially, append-only bounded media/evidence files outside relational rows. Industrial PostGIS can index road/zone/vehicle geometry with explicit coordinate systems; object storage retains high-rate media. Redis is optional latest-state cache, not authoritative history. No industrial database dependency is imposed on the current prototype.
