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
| disconnect/reconnect | portable service/session reset and host transport flush tested; physical USB binding pending | software evidence in Protocol V2 tests; no board verification |
| hardware watchdog / task stall | requires ESP-IDF task integration | not yet verified |
