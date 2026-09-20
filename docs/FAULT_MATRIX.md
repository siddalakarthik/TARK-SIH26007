# Fault Matrix

| Fault | Implemented response | Evidence status |
|---|---|---|
| malformed SIM1 frame | parser raises explicit FrameError | tested |
| missing/stale sensor evidence | UNKNOWN with zero Phase 1 permitted speed | tested |
| non-closing track | TTC_NOT_APPLICABLE | implemented |
| corrupt protocol frame | decoder rejects CRC/COBS failure | tested |
| expired/out-of-order command | ESP32 client rejects | tested |
| browser/API loss | no control route exists; decision pipeline independent | tested by route scan |
| real serial disconnect | adapter raises explicit error for orchestration health handling | not hardware verified |
| database failure | EventStore exception must be surfaced; no fabricated event | not injected yet |

Simulation testing is not hardware validation.

