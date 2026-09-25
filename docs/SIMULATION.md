# Simulation and Hardware Interface Testing

`SIMULATION` is the default development source. The integrated system emits deterministic radar tracks, decision outputs, zero-output Phase 1 commands, ESP32 status, sensor availability and event records. Phase 2 devices are either `SIMULATION` or `NOT_CONNECTED_PHASE_2`; no simulated value may be called live.

`REPLAY` consumes preserved recorded inputs through the same parser/pipeline but has no ESP32 command sink. `REAL_HARDWARE` remains a configuration selection that must be blocked by verified device discovery and purchased documentation. No source switch may rewrite the PV-SOE domain pipeline.

Run `scripts/run.ps1`, open `http://localhost:8000/api/v1/status`, and inspect the `mode`, `traction`, source modes, sensor status, state/reason and events. The browser UI source is under `frontend/`; production bundles are served by FastAPI once its dependency build succeeds.

## Phase-1 integrity correction

The existing single-process launch now runs one FastAPI-lifespan decision task,
with a nominal 250 ms interval after each completed step (no catch-up bursts).
REST and WebSocket readers consume detached snapshots; polling does not create
commands/events or move the GNSS simulator. With no observers, execution still
continues. Do not launch multiple application workers against one vehicle.
An unstarted/failed/stale runtime returns 503 from status/readiness; WebSocket
publication closes with 1013. A cached NORMAL snapshot also expires when its
supporting radar evidence crosses the existing stale boundary.

Retained radar input scenarios: `TARGET_APPROACH`, `FAST_TARGET_APPROACH`,
`TARGET_RECEDING`, `MULTI_TARGET`, `RADAR_LOSS`, `RADAR_STALE`. With the reviewed
Phase-1 configuration, the target scenarios produce NORMAL; no-report scenarios
produce UNKNOWN from an empty pipeline and follow existing freshness after a
prior report. These names describe inputs, not forced output states.
`NORMAL`, `WARN`, `RESTRICT`, `UNKNOWN`, `STOP` are rejected as scenario names;
the old misleading STOP fixture is now FAST_TARGET_APPROACH with the same
velocity input. WARN SEMANTICS NOT YET DEFINED IN PRODUCTION CONTRACT.

Measured vehicle speed is UNAVAILABLE; TTC is NOT COMPUTED. The decision's
existing zero-speed assumption is not a physical speed measurement. Commanded
permitted speed and both wheel commands remain zero. Recording writes are
blocked server-side in the public_demo deployment environment; existing local
and authenticated operator workflows remain available.

See SOFTWARE_INTEGRITY_CORRECTION_REPORT.md for executable reproduction and
regression evidence. Replay's deeper semantic corrections remain deferred.
