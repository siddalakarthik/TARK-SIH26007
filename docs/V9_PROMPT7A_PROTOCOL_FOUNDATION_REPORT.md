# V9 Prompt 7A — Protocol V1 Interoperability Foundation

## Scope

This atomic pass was limited to Protocol V1 framing, canonical vectors and
Python/C firmware-host interoperability. It did not add or enable physical
serial communication, GPIO, PWM, MDD10A control, encoder capture or traction.

## Completed before continuation

The interrupted pass had added the Python Protocol V1 framing client,
bounded frame accumulator, simulator-side ACK/NACK behavior, C COBS encoder,
and a bounded firmware CBOR COMMAND validator. It also identified a host-test
failure while exercising a cross-language STATUS vector.

## Defects corrected

The firmware frame decoder incorrectly treated its 24-byte envelope and
4-byte CRC as if the payload length included CRC. It also decoded the wire
sequence/timestamp offsets as a 32-bit sequence plus timestamp at offset 12,
while the actual `!HBBIQQ` envelope has 64-bit slots at offsets 8 and 16.
The decoder now uses the correct 28-byte minimum (`header + CRC`), payload
length check, offsets and payload start. COMMAND semantic sequence range still
remains uint32 as specified.

## Canonical artifacts

- `docs/ESP32_PROTOCOL_V1.md` — authoritative V1 contract.
- `protocol_vectors.json` — canonical COMMAND, ACK, NACK, STATUS and boundary
  HEARTBEAT expected CBOR, CRC32C and COBS bytes.
- `scripts/generate_protocol_vectors.py` — deterministic C-header generator.
- `firmware/esp32/tests/protocol_vectors.h` — generated C host-test input.

Python consumes the JSON directly. C consumes the generated header and checks
all five frame envelopes, command CBOR semantics, CRC-32C and COBS round trip.

## Task 7B remains

Task 7B should implement and test firmware-side CBOR response encoding and
the actual USB RX/TX loop using the frozen contract. It must retain the
identity gate and `DISABLED_PHASE_1` zero-output latch. Hardware verification
remains completely pending.
