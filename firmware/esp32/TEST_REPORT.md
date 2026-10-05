# Test Report

> HISTORICAL BASELINE — SUPERSEDED BY LATER RED-TEAM / CORRECTION RELEASE.
> Retained as a dated record, not current completion or protocol authority.
> Use [R1 release index](../../docs/TARK_RELEASE_INDEX.md),
> [Protocol V2](../../docs/ESP32_PROTOCOL_V2.md) and
> [supersession register](../../docs/TARK_SUPERSESSION_REGISTER.md).

## Executed

| Suite | Result |
|---|---|
| ESP32 host CRC-32C known-answer test | PASS |
| ESP32 command first/duplicate/expired/heartbeat cases | PASS |
| Pi Python suite | PASS - 10 tests |

## Defect found and fixed

The initial host test labelled a command expired while its `valid_until` timestamp was still later than `now`. The implementation correctly accepted it; the test vector was corrected to make `valid_until <= now`. This regression remains in `tests/host_test.c`.

## Not executed

ESP-IDF build, board flash, USB enumeration, physical Pi-to-ESP32 traffic, watchdog facilities, heap/stack measurement, soak testing, and physical hardware tests are **NOT YET VERIFIED** because the ESP-IDF SDK and exact purchased board hardware were not available in this environment.
