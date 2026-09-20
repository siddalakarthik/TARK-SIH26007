#include "esp_log.h"
#include "command/command_supervisor.h"
#include "status/status.h"
#include "safety/watchdog.h"
void app_main(void){command_supervisor_t supervisor; tark_status_t status; tark_watchdog_t watchdog; command_supervisor_init(&supervisor);tark_status_init(&status);tark_watchdog_init(&watchdog,0);ESP_LOGI("TARK","boot firmware=%s protocol=%u outputs=%s watchdog=%s",status.firmware_version,status.protocol_version,status.output_status,watchdog.state);/* USB transport and hardware watchdog binding are deliberately not connected to board-specific ESP-IDF drivers until exact DevKitC-1 documentation is reviewed. */}
