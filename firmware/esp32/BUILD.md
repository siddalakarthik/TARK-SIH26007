# Build and Test

## Host protocol test

From `tark` on a machine with GCC:

```powershell
gcc -std=c11 -Wall -Wextra -Werror -I firmware/esp32/main/protocol -I firmware/esp32/main/command firmware/esp32/tests/host_test.c firmware/esp32/main/protocol/tark_protocol.c firmware/esp32/main/command/command_supervisor.c -o firmware/esp32/tests/host_protocol_tests.exe
.\firmware\esp32\tests\host_protocol_tests.exe
```

## ESP-IDF build and flash

After installing the ESP-IDF version approved for the purchased ESP32-S3 board and exporting its environment:

```powershell
cd firmware/esp32
idf.py set-target esp32s3
idf.py build
idf.py -p <verified_usb_serial_port> flash monitor
```

`<verified_usb_serial_port>` must come from the actual board/USB enumeration. Do not guess a port or USB controller configuration. A successful build or flash is not physical traction validation.

