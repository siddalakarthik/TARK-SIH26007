# Known Limitations

- Phase 1 traction remains disabled by hard command outputs of zero.
- The vendor LD2450 binary frame format was not supplied, so real raw serial capture exists but real normalized parsing requires a reviewed decoder.
- PV-SOE timing, deceleration and margin values are `PARAMETERIZED / NOT VALIDATED`.
- Physical USB/ESP32 exchange, MDD10A GPIO/PWM binding and encoder GPIO interrupt capture require verified boards and documentation. The software boundaries and safe Phase-1 host tests exist, but are not physical verification.
- Simulation/replay tests are not physical validation.
- SQLite event persistence, bounded observation recording, replay-session selection, deterministic normalized replay timelines, seeking, stepping and replay verification are active. Raw LD2450 bytes may be retained as evidence but remain deliberately non-replayable until a reviewed vendor decoder exists.
- BNO055 and MLX90640 have optional-library read-once adapters with strict normalized-sample/frame validation. Their physical identity, bus/address, library/device compatibility, calibration, mounting and live readings remain unverified.
- The physical E-stop remains independent hardware; this backend neither replaces nor verifies it.
