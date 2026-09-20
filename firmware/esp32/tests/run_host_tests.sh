#!/usr/bin/env sh
set -eu
gcc -std=c11 -Wall -Wextra -Werror -I main/protocol -I main/command -I main/hardware -I main/safety tests/host_test.c main/protocol/tark_protocol.c main/protocol/command_payload.c main/command/command_supervisor.c main/hardware/motor_driver.c main/hardware/encoder.c main/safety/watchdog.c -lm -o /tmp/tark_esp32_host_tests
/tmp/tark_esp32_host_tests
