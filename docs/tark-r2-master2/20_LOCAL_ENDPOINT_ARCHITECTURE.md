# 20 — Local endpoint and Protocol V2 migration

The sole current contract is [Protocol V2](../ESP32_PROTOCOL_V2.md). Do not modify R1 or claim the reported ASCII robot implements V2.

## Existing software versus future physical binding

Existing portable software validates COBS, CRC32C, strict canonical CBOR, exact schemas, session/configuration, sequence, lifetime, ACK/NACK/STATUS and zero-output supervision. Maximum frame 640 bytes, payload 512 bytes, duration <=500 ms. Unique-per-boot identity plus new session generation rejects old sessions. Host/receiver monotonic epochs are not compared. CRC is not cryptographic authentication.

Future binding must supply verified board transport RX/TX/disconnect, a fresh boot identity, serialized event ownership, periodic supervision tick and reviewed hardware watchdog. No guessed USB stack/port, entropy source or task period is inserted here. Hardware watchdog tests must establish outputs during reset/boot, not only task liveness.

Receive bytes → bounded frame validation → canonical payload validation → session/sequence/configuration/lifetime checks → local supervisor → ACK/NACK and periodic STATUS. Callback TX is bounded; a blocked transmitter cannot prevent independent expiry. Heartbeats never renew a command. Reconnect clears partial buffers/pending commands and requires a new session.

V2 lifetime bounds time *after reception*; it does not establish original age across unknown transport delay. Therefore future positive-output R2 requires an approved additional age/latency argument (measured bounded path or explicitly reviewed deadline/session revision). Do not claim 500 ms end-to-end physical freshness from the current duration field.

## Wheel and actuator migration

Current STATUS has no wheel payload. Specify a future WHEEL_RESPONSE contract through the same service/codec/transport: source epoch/sample sequence, left/right angle and validity, sample times/clock mapping, wheel response estimates, diagnostics and configuration identity. No numeric message ID or undeclared V2 field is assigned here. Version/schema review must update host, firmware, shared vectors, logging/replay and compatibility tests together; legacy/current-incompatible frames must fail clearly.

Existing ENA/ENB jumpers and uncertain right GPIO are not a released variable-speed drive. A later board profile must define fail-disabled enable/direction sequencing, reversal dead-time appropriate to hardware, output reset/brownout behavior and calibrated command-to-response limits. Positive commands require separately authorized phase and physical gates. No browser or replay object can construct that authority.

## Migration gates

1. Archive exact ASCII sketch/hash and as-built wiring; no parallel command authority.
2. Confirm board/ports/pins and logic voltages with traction disconnected.
3. Bind reviewed V2 service with zero outputs; prove sessions/expiry and callback scheduling using host then bench evidence.
4. Review/version wheel telemetry and any positive-authority age changes; shared-vector regression.
5. Qualify physical independent cutoff, reset-inhibited driver and actual wheel/motor response under separate authorization.
6. Only then consider a phase-bound model motion release; remain DISABLED_PHASE_1 otherwise.

ACK means accepted software request, not physical action. STATUS means telemetry, not ACK/freshness renewal. SOFTWARE STOP is distinct from physical traction power interruption, and neither alone establishes stopping distance.
