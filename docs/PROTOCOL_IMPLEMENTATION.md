# Protocol Implementation

Implemented Protocol V1 software contract: USB CDC transport boundary, `0x00` COBS delimiters, big-endian fixed header, canonical CBOR payload and CRC-32C. The implementation encodes the required Phase 1 command fields and rejects malformed framing, CRC failure, expired sequence, non-increasing sequence and negative permitted speed. Python and firmware host tests share canonical command, ACK, NACK, STATUS and heartbeat vectors.

This is a **SOFTWARE IMPLEMENTATION DETAIL — PHYSICAL VERIFICATION REQUIRED**. The physical documents freeze the USB link and required fields, not this encoding. Firmware source implements bounded command decoding and ACK/NACK/STATUS encoding with Phase-1 zero outputs; physical USB enumeration, flashing, clock behavior and watchdog behavior remain hardware verification items. Retransmission/clock-offset policy remains intentionally outside the present Phase-1 transport contract.
