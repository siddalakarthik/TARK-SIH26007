# 03 — ESP32 GPIO reservation

DESIGN ONLY. Reported MCU/PSRAM identity does not prove PCB pin routing.

## Inspected evidence

Master-1 supersedes older Batch-A claims that GPIO16/17 are final. GPIO4→IN1 and GPIO5→IN2 remain reported connections. Current firmware app_main has no physical USB or unique boot-identity binding. No physical ASCII sketch was found in the inspected firmware tree; obtain its source/hash. A reported ASCII timeout is not Protocol V2 verification. Old R1 MDD10A/quadrature mappings are not R2 L298N/SPI mappings.

| Logical function | Direction | Required capability | Candidate GPIO | Reason | Conflict | Validation |
|---|---|---|---|---|---|---|
| MOTOR_L_A | OUT | Inactive at reset | GPIO4 reservation only | Existing IN1 | Old encoder map | Board/trace/source |
| MOTOR_L_B | OUT | Inactive at reset | GPIO5 reservation only | Existing IN2 | Old encoder map | Board/trace/source |
| MOTOR_R_A | OUT | Inactive at reset | NONE; GPIO16 under investigation | Logical IN3 | Board unknown | Resolve investigation |
| MOTOR_R_B | OUT | Inactive at reset | NONE; GPIO17 under investigation | Logical IN4 | Board unknown | Resolve investigation |
| ENC_LEFT_CS | OUT | Independent SPI select | PHYSICAL PIN CONFIRMATION REQUIRED | Left channel | Motor/memory reservations | Exact free-pin map |
| ENC_RIGHT_CS | OUT | Independent SPI select | PHYSICAL PIN CONFIRMATION REQUIRED | Right channel | Same | Same |
| SPI_SCLK | OUT | Hardware SPI | PHYSICAL PIN CONFIRMATION REQUIRED | Clock | Flash/PSRAM/mux | Board and bus test |
| SPI_MISO | IN | Hardware SPI | PHYSICAL PIN CONFIRMATION REQUIRED | Angle response | Carrier tri-state | Two-device bus |
| SPI_MOSI | OUT | Hardware SPI | PHYSICAL PIN CONFIRMATION REQUIRED | Read commands | Carrier protocol | Datasheet/profile |
| BUZZER | OUT | Digital pattern | PHYSICAL PIN CONFIRMATION REQUIRED | Assembled module | Boot level/current | Input/driver review |
| STATUS | OUT if fitted | Existing indicator | PHYSICAL PIN CONFIRMATION REQUIRED | Diagnostics | LED type unknown | Polarity and mapping |
| Future spare | Unassigned | No enabled function | None | Reserve | All existing uses | Review before use |
| MOTOR_L_ENABLE / MOTOR_R_ENABLE | OUT, future gated design | Fail-disabled/PWM | PHYSICAL PIN CONFIRMATION REQUIRED | Existing jumpers insufficient | Deliberate wiring change | Reset/current/PWM tests |

MOTOR_L_A/B and MOTOR_R_A/B are logical aliases of earlier MOTOR_IN1/2/3/4, not a new physical assignment. Do not reuse GPIO4/5/16/17 for wheels or buzzer.

Screen exact board schematic against [Espressif](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/gpio.html): boot straps, flash/PSRAM nets, LEDs, UART/JTAG and USB. GPIO19/20 have native USB functions; alternative USB-UART use does not automatically release those pins. Memory restrictions depend on the actual module.

Final record requires header label, SoC GPIO, voltage, reset state, pull network, conflict and firmware symbol. Verify unpowered continuity, then separately authorized logic tests with traction disconnected. Jetson/BNO085 SPI and ESP/wheel SPI are separate buses. No candidate is an instruction to move a wire.
