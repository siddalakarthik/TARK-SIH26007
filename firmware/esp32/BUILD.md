# Build and Test

## Host protocol test

From the repository root in the installed project Python environment, with
GCC available and hardware configuration unset:

```powershell
python -B -m pytest -q -p no:cacheprovider backend/tests/test_protocol_correctness.py
```

The existing fixture compiles fresh protocol, service/supervisor and interop
executables with all required sources using `-std=c11 -Wall -Wextra -Werror`.
It executes both host suites and Python/C cases. The older one-line link
command omitted required implementation sources and is superseded by this
tested workflow. On POSIX, `sh firmware/esp32/tests/run_host_tests.sh` is also
provided. Report application-control denials rather than disabling OS policy.

## ESP-IDF build and flash — future gated hardware work

Not executed or authorized by the software-evidence release. The current
entrypoint stays UNAVAILABLE_HARDWARE_BINDING_PENDING. A reviewed board
RX/TX, unique boot identity, scheduling/disconnect and hardware-watchdog binding
is required before claiming a communicating board. After separate approval,
install the ESP-IDF version approved for that board and export its environment:

```powershell
cd firmware/esp32
idf.py set-target esp32s3
idf.py build
idf.py -p <verified_usb_serial_port> flash monitor
```

`<verified_usb_serial_port>` must come from the actual board/USB enumeration. Do not guess a port or USB controller configuration. A successful build or flash is not physical traction validation.
