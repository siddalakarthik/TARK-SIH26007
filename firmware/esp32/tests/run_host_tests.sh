#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
# Unique temporary outputs; never execute stale repository binaries.
build_dir=$(mktemp -d "${TMPDIR:-/tmp}/tark-protocol-host.XXXXXX")
for test_name in host_test task7b_host_test interop_host; do
    "${CC:-gcc}" -std=c11 -Wall -Wextra -Werror "tests/$test_name.c" \
        main/protocol/tark_protocol.c main/protocol/command_payload.c \
        main/protocol/response.c main/protocol/service.c \
        main/command/command_supervisor.c main/hardware/motor_driver.c \
        main/hardware/encoder.c main/safety/watchdog.c -lm \
        -o "$build_dir/$test_name"
done
"$build_dir/host_test"
"$build_dir/task7b_host_test"
printf 'Fresh host binaries: %s\n' "$build_dir"
# interop_host consumes bounded stdin fixtures from test_protocol_correctness.py.
