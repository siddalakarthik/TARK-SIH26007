# Fault Matrix

| Fault | Implemented response | Evidence status |
|---|---|---|
| malformed SIM1 frame | parser raises explicit FrameError | tested |
| missing/stale sensor evidence | UNKNOWN with zero Phase 1 permitted speed | tested |
| non-closing track | TTC helper returns NOT_APPLICABLE; production policy does not invoke TTC | helper only, not a production-state transition |
| corrupt protocol frame | decoder rejects CRC/COBS failure | tested |
| expired/out-of-order command | ESP32 client rejects | tested |
| browser/API loss or extra observers | one lifespan owner continues; observers read snapshots and cannot create ticks | deterministic zero/one/multiple observer and reconnect-storm tests |
| invalid future/negative observation timestamp | reject evidence; FAILED/STALE health and UNKNOWN decision until valid evidence | strict no-tolerance boundary tests |
| runtime unavailable or expired NORMAL evidence at publication | status/readiness 503; WebSocket 1013; HMI clears current-looking values | lifecycle, publication-boundary and reconnect regressions |
| public-demo recording mutation | server-side 403; no session mutation | API regression; local/authenticated workflow retained |
| real serial disconnect | adapter raises explicit error for orchestration health handling | not hardware verified |
| database failure | EventStore failure surfaces; runtime/status/readiness become unavailable without increased authority | Prompt-3 negative control and harness tests |

Simulation testing is not hardware validation.
