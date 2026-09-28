# Simulation and Hardware Interface Testing

`SIMULATION` is the default development source. The integrated system emits deterministic radar tracks, decision outputs, zero-output Phase 1 commands, ESP32 status, sensor availability and event records. Phase 2 devices are either `SIMULATION` or `NOT_CONNECTED_PHASE_2`; no simulated value may be called live.

Recorded-session replay reconstructs an isolated production Pipeline from normalized
format-2 inputs/checkpoints; it has no ESP32 command sink. This is distinct from
the application's `replay` runtime mode, which disables physical startup and is
used by the offline evidence harness with injected protocol fixtures. The actual
mode values are `simulation`, `replay` and `real_radar`; `REAL_HARDWARE` is not a
CLI mode. Physical adapters require their configured/identity-reviewed boundaries.
No source switch rewrites the PV-SOE domain pipeline.

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

See [Prompt-1 evidence](SOFTWARE_INTEGRITY_CORRECTION_REPORT.md),
[current replay semantics](REPLAY_GUIDE.md) and
[Prompt-3 evidence](DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md). Recording-format-2
checkpoint, batch, valid-empty and full-session corrections are implemented;
no claim is made for deterministic reconstruction of legacy recordings.
