idf_component_register(
    SRCS "app_main.c" "protocol/tark_protocol.c" "protocol/command_payload.c" "protocol/response.c" "protocol/service.c" "command/command_supervisor.c"
         "status/status.c" "hardware/motor_driver.c" "hardware/encoder.c" "safety/watchdog.c"
    INCLUDE_DIRS "." "hardware"
)
