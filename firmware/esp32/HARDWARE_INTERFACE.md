# Hardware Interface

USB is the intended Pi-to-ESP32 physical transport, not verified board operation.
The current [Protocol V2](../../docs/ESP32_PROTOCOL_V2.md) host/C boundary is
implemented; actual board binding remains unavailable. No Pi GPIO UART, SPI
or I2C control link is added. Exact USB configuration requires purchased-board documentation.

Phase 2 mappings from the [controlled electrical design](../../release/references/README.md)
remain intended interfaces within HOLD limits: GPIO4/5 left encoder A/B,
GPIO6/7 right encoder A/B, GPIO9 PWM1 to MDD10A P4, GPIO10 DIR1 to P5,
GPIO11 PWM2 to P2, GPIO12 DIR2 to P3, J1-22 ground to MDD10A P1, and GPIO13
auxiliary E-stop/contactor status only. Encoder VCC remains TBD/VERIFY.
No motor, encoder, MDD10A or E-stop output is enabled by this Phase 1 firmware.

`main/hardware/motor_driver.*` is the bounded MDD10A software boundary. It records a clamped request but applies zero output and returns `false` while `DISABLED_PHASE_1` is active. It intentionally contains no ESP-IDF GPIO/PWM binding. `main/hardware/encoder.*` is the wheel-response data boundary. Its present count function is explicitly for simulation/host-test use; it is not an interrupt driver and it never calls the result ground speed. GPIO capture may only be added after the actual encoder output interface and VCC are verified.

`main/safety/watchdog.*` is a tested software watchdog boundary. It tracks kicks and expiry without registering a physical ESP-IDF watchdog. Registration, timeout tuning and reset behavior remain `NOT PHYSICALLY VERIFIED` until the firmware is flashed on the exact board and the scheduler/watchdog configuration is reviewed.
