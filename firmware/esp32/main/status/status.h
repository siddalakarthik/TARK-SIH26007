#pragma once
#include <stdint.h>
typedef struct { const char *firmware_version; uint8_t protocol_version; const char *configuration_hash; const char *output_status; uint32_t last_sequence; const char *last_rejection; } tark_status_t;
void tark_status_init(tark_status_t *s);
