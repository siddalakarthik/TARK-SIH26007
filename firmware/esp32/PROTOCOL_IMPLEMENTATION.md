# Protocol Implementation

The C implementation follows the development baseline used by the Pi: sentinel `0x00`, COBS encoding, big-endian header, payload length protection and CRC-32C. CRC-32C uses reflected Castagnoli polynomial `0x82F63B78`, initial value `0xFFFFFFFF`, reflected processing and final XOR/inversion; the standard `123456789` known answer is `0xE3069283`.

The authoritative current V2 contract is
[`../../docs/ESP32_PROTOCOL_V1.md`](../../docs/ESP32_PROTOCOL_V1.md)
(historical filename retained). Legacy V1 frames are rejected.
The firmware host boundary independently decodes the fixed envelope and a
bounded canonical CBOR COMMAND map, consuming vectors generated from the
single `protocol_vectors.json` source. It validates required fields, types,
ranges, matching header sequence/timestamp, configuration hash, session and
bounded sender lifetime converted to receiver-local expiry
before the command supervisor can accept it.

Firmware-side ACK/NACK/STATUS CBOR generation and the injected bounded RX/TX
service are implemented and shared-vector tested. Firmware responses identify
the production endpoint as `REAL`; the separate Python simulator is the only
endpoint labelled `SIMULATION`. Board-specific USB RX/TX binding, device
identity evidence and physical ESP32, watchdog, motor, encoder or E-stop
operation remain unverified. The independent service tick supervises expiry
without incoming frames and emits periodic STATUS. Disconnect retires the
session; every valid SESSION_OPEN gets a new receiver generation. A reviewed
board binding must provide a fresh unique boot identity, serialized RX/tick/
disconnect calls, TX and periodic scheduling. Missing binding stays unavailable.

Canonical CBOR uses a bounded flat ASCII-keyed map, shortest integer/finite
binary16/32/64 encodings and exact schemas. The fresh host interoperability
harness checks Python commands through the C supervisor and C responses back
through Python correlation, in addition to the shared byte/semantic vectors.
