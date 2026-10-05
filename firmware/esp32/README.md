# TARK ESP32 S3 Phase 1 Firmware

This ESP-IDF C project is the bounded command-validation and status layer for the TARK research prototype. `app_main` initializes disabled board-neutral state and logs `UNAVAILABLE_HARDWARE_BINDING_PENDING`; it does not establish physical identity or start a guessed USB service. It does not enable motor or traction outputs, replace the physical E-stop, or calculate perception, TTC or PV-SOE.

The current V2 development contract implements COBS framing, CRC-32C, canonical CBOR validation, session/sequence supervision, bounded receiver-local expiry, heartbeat age and Phase-1 disabled output status. Its receive/disconnect/periodic-tick/TX boundary is host-tested. USB binding, fresh boot identity, scheduling and the physical watchdog must be supplied by a reviewed board adapter; the entrypoint remains unavailable until then.

The approved versioned software contract is in [the protocol specification](../../docs/ESP32_PROTOCOL_V2.md). It is not an electrical or physical validation claim. Run `sh firmware/esp32/tests/run_host_tests.sh` from the repository root with GCC available, or run the Python interoperability test fixture; both compile fresh strict-warning host binaries. No hardware is accessed.
