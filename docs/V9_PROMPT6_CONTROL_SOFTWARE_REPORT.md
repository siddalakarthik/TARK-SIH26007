# V9 Prompt 6 Control Software Report

## Implemented in this pass

- Hardened Pi protocol client validation for uint32 sequences, finite bounded
  values, command ranges, expiry and ordering.
- Added structured ACK/NACK/STATUS parsing. Feedback is telemetry and is never
  interpreted as proof of physical output.
- Added a deterministic Pi↔ESP32 protocol simulator that reports
  `DISABLED_PHASE_1` with applied outputs fixed at zero, including
  configuration-mismatch and replay rejection paths.
- Added an identity-gated USB serial transport. It performs discovery without
  identification and refuses opening until the operator records evidence and
  supplies reviewed path/baudrate values.
- Added firmware safe-stop state recording while preserving the permanent
  Phase-1 output-disable latch.
- Extended Python and firmware-host regression coverage.

## Tests run

- `python -m pytest backend/tests/test_protocol.py backend/tests/test_esp32_usb.py -q`
- Windows-equivalent GCC invocation of `firmware/esp32/tests/run_host_tests.sh`

The GCC host test validates CRC-32C, duplicate/expired sequences, forced safe
stop latch, disabled motor output, simulated encoder freshness and watchdog
expiry. It is not an ESP-IDF build or hardware test.

## Remaining hardware-dependent work

Board-specific USB serial selection/baudrate, firmware flashing, CBOR payload
parsing on flashed firmware, physical watchdog configuration, MDD10A output,
encoder interface and E-stop/contactor validation remain unverified. Traction
must remain disabled until an explicit later physical validation phase.
