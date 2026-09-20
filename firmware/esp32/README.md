# TARK ESP32 S3 Phase 1 Firmware

This ESP-IDF C project is the bounded command-validation and status layer for the TARK research prototype. At boot it reports identity and enters `DISABLED_PHASE_1`. It does not enable motor or traction outputs, does not replace the physical E-stop, and does not calculate perception, TTC or PV-SOE.

The current development baseline implements COBS framing, CRC-32C, binary envelope validation, monotonic sequence supervision, expiry, heartbeat age and Phase 1 disabled output status. USB binding is intentionally not tied to a board-specific ESP-IDF USB facility until the exact purchased ESP32-S3 DevKitC-1 documentation is reviewed.

The protocol is a **PROPOSED SOFTWARE CONTRACT - DEVELOPMENT BASELINE**. It is not defined by the electrical schematic.

