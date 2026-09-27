# Known Limitations

- This is a research-prototype firmware boundary, not safety-certified.
- The ESP-IDF project has not been built/flashed in this environment.
- Exact USB transport selection and board identity/firmware-version evidence are pending purchased-board documentation and controlled bring-up.
- Protocol V2 canonical CBOR, session-bound commands/responses, receiver-local expiry and shared Python/C vectors are implemented and host-tested. V1 is rejected; both peers must be upgraded together.
- The board-neutral periodic supervisor is implemented. Actual USB RX/TX, a unique-per-boot identity source, serialized scheduling/disconnect hooks and hardware watchdog binding remain unavailable pending reviewed board integration. `app_main` does not pretend these exist.
- Session/CRC validation is not cryptographic authentication or a physical latency guarantee.
- No physical E-stop substitution, encoder electrical capture, MDD10A control, motor output or traction validation has been performed.
- Phase 1 output status is `DISABLED_PHASE_1`.
- Any Phase 2 motor safe-output behaviour requires hardware verification; no PWM/brake/coast claim is made here.
