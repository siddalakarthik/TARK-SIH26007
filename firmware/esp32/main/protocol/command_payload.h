#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Minimal bounded CBOR validator for the Protocol V1 COMMAND map. It supports
 * only the definite-length map/text/integer/float/null forms emitted by the
 * canonical Pi encoder; unknown/indefinite forms are rejected. */
typedef struct { uint64_t valid_until_ns; float permitted_speed_mps,left_command,right_command; uint32_t heartbeat; bool valid; } tark_command_payload_t;
bool tark_validate_command_cbor(const uint8_t *data,size_t length,uint64_t sequence,uint64_t timestamp_ns,uint64_t now_ns,const char *configuration_hash,tark_command_payload_t *out);
bool tark_validate_heartbeat_cbor(const uint8_t *data,size_t length,const char *configuration_hash);
/* 0 absent/malformed, 1 matching, 2 explicitly mismatched. */
int tark_command_configuration_state(const uint8_t *data,size_t length,const char *configuration_hash);
