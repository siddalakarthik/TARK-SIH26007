# Simulation and Hardware Interface Testing

`SIMULATION` is the default development source. The integrated system emits deterministic radar tracks, decision outputs, zero-output Phase 1 commands, ESP32 status, sensor availability and event records. Phase 2 devices are either `SIMULATION` or `NOT_CONNECTED_PHASE_2`; no simulated value may be called live.

`REPLAY` consumes preserved recorded inputs through the same parser/pipeline but has no ESP32 command sink. `REAL_HARDWARE` remains a configuration selection that must be blocked by verified device discovery and purchased documentation. No source switch may rewrite the PV-SOE domain pipeline.

Run `scripts/run.ps1`, open `http://localhost:8000/api/v1/status`, and inspect the `mode`, `traction`, source modes, sensor status, state/reason and events. The browser UI source is under `frontend/`; production bundles are served by FastAPI once its dependency build succeeds.
