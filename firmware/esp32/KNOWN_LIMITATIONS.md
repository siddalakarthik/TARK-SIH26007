# Known Limitations

- This is a research-prototype firmware boundary, not safety-certified.
- The ESP-IDF project has not been built/flashed in this environment.
- Exact USB transport selection is pending purchased-board documentation.
- Protocol V1 canonical CBOR validation and shared Python/C host vectors are implemented and software-tested.
- No physical E-stop substitution, encoder processing, MDD10A control, motor output or traction validation has been performed.
- Phase 1 output status is `DISABLED_PHASE_1`.
- Any Phase 2 motor safe-output behaviour requires hardware verification; no PWM/brake/coast claim is made here.
