#include "esp_log.h"
#include "protocol/service.h"
#include "status/status.h"
#include "safety/watchdog.h"
void app_main(void){
    static tark_protocol_service_t service;
    tark_status_t status;tark_watchdog_t watchdog;
    tark_status_init(&status);tark_watchdog_init(&watchdog,0);
    /* No guessed USB driver, boot-identity entropy source, task period or
     * hardware watchdog binding. A reviewed board adapter must supply a fresh
     * boot identity, RX/TX, disconnect notification and periodic tick calls.
     * Until then this entrypoint remains explicitly unavailable/non-actuating. */
    tark_protocol_service_init(&service,status.configuration_hash,NULL,NULL,NULL);
    tark_protocol_service_tick(&service,0);
    ESP_LOGI("TARK","firmware=%s protocol=%u outputs=%s transport=UNAVAILABLE_HARDWARE_BINDING_PENDING",status.firmware_version,status.protocol_version,status.output_status);
}
