# Known Limitations

Current authority: [R1 claim matrix](TARK_CLAIM_EVIDENCE_MATRIX.md).

- Production `D_env` is nearest active radar range minus stored uncertainty,
  not a calibrated free-space/corridor observability envelope. Radar slot IDs
  do not guarantee physical target identity; no EKF/fusion runs in production.
- Production stopping assumes zero vehicle speed. TTC helper exists but is
  not integrated into production decisions; HMI says NOT COMPUTED. WARN has
  no executable production policy. AGING may retain NORMAL under current rules.
- Communication loss expires supervision/feedback but is not a new PV-SOE
  transition policy; the last generated state can remain NORMAL with failed
  link health. All commands are nevertheless permanently zero in Phase 1.
- Sensor identity review, per-adapter I2C access/serialization, GNSS UTC
  aggregation and long-duration event retention remain bounded implementation
  limitations, not field-validated capabilities. Prompt 4 does not expand them.

- Phase 1 traction remains disabled by hard command outputs of zero.
- The documented LD2450 target-report decoder is software-tested, but actual receiver identity, serial communication, mounting, target quality and calibration are not physically verified. Undocumented LD2450 frame types and configuration commands are intentionally unsupported.
- PV-SOE timing, deceleration and margin values are `PARAMETERIZED / NOT VALIDATED`.
- Physical USB/ESP32 exchange, MDD10A GPIO/PWM binding and encoder GPIO interrupt capture require verified boards and documentation. The software boundaries and safe Phase-1 host tests exist, but are not physical verification.
- Simulation/replay tests are not physical validation.
- SQLite event persistence, bounded observation recording, replay-session selection, deterministic normalized replay timelines, seeking, stepping and replay verification are active. Raw LD2450 bytes remain diagnostic evidence; decoded normalized observation ticks are replayable.
- BNO055 and MLX90640 have optional-library read-once adapters with strict normalized-sample/frame validation. Their physical identity, bus/address, library/device compatibility, calibration, mounting and live readings remain unverified.
- The physical E-stop remains independent hardware; this backend neither replaces nor verifies it.
