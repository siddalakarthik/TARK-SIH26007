# Fault Matrix

| Condition | Current response | Test status |
|---|---|---|
| bad magic, length, COBS or CRC-32C | protocol decoder rejects | host code implemented; CRC tested |
| unsupported version/type | protocol decoder rejects | implemented |
| duplicate sequence | reject | tested |
| old sequence | reject | implemented |
| expired command | reject | tested |
| configuration mismatch | reject | implemented |
| heartbeat timeout | communication authority invalid | tested at supervisor level |
| Phase 1 output request | output remains disabled | status/initialization implemented |
| USB disconnect/reconnect | requires USB transport integration | not yet verified |
| hardware watchdog / task stall | requires ESP-IDF task integration | not yet verified |

