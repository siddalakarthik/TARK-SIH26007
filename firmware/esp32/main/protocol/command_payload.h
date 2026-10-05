#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Bounded V2 canonical flat-map profile: unsigned/signed numeric values,
 * shortest finite IEEE float16/32/64, ASCII tokens, boolean/null. */
#define TARK_MAX_COMMAND_LIFETIME_NS 500000000ull
typedef struct { uint64_t valid_until_ns,local_expiry_ns; double permitted_speed_mps,left_command,right_command; uint32_t heartbeat; bool valid; const char *reason; } tark_command_payload_t;
bool tark_validate_command_cbor(const uint8_t *data,size_t length,uint64_t sequence,uint64_t timestamp_ns,uint64_t now_ns,const char *configuration_hash,const char *session_id,tark_command_payload_t *out);
bool tark_validate_heartbeat_cbor(const uint8_t *data,size_t length,const char *configuration_hash,const char *session_id);
bool tark_session_request_cbor(const uint8_t *data,size_t length,const char *configuration_hash,char request_id[33]);
bool tark_canonical_map(const uint8_t *data,size_t length);
