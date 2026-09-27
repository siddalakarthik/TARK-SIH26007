#pragma once
#include <stdbool.h>
#include <stdint.h>
typedef enum { CMD_RECEIVED, CMD_VALIDATED, CMD_ACCEPTED, CMD_APPLIED, CMD_REJECTED } command_state_t;
typedef enum { NACK_NONE, NACK_DUPLICATE_SEQUENCE, NACK_OLD_SEQUENCE, NACK_OUT_OF_ORDER_SEQUENCE, NACK_EXPIRED_COMMAND, NACK_HEARTBEAT_TIMEOUT, NACK_CONFIGURATION_MISMATCH, NACK_NOT_ENABLED, NACK_INTERNAL_FAULT } command_reject_t;
typedef struct { bool seen; uint32_t last_sequence; uint64_t heartbeat_ns,local_expiry_ns; bool active; bool phase1_output_disabled; const char *last_rejection; } command_supervisor_t;
void command_supervisor_init(command_supervisor_t *s);
command_reject_t command_supervisor_accept(command_supervisor_t *s,uint32_t sequence,uint64_t now_ns,uint64_t valid_until_ns,bool config_match);
bool command_supervisor_heartbeat_expired(const command_supervisor_t*s,uint64_t now_ns,uint64_t timeout_ns);
/* This is a software state transition only. It never changes the Phase-1
 * output-disable latch and must be invoked only after protocol validation. */
void command_supervisor_force_safe_stop(command_supervisor_t *s, command_reject_t reason);
void command_supervisor_tick(command_supervisor_t *s,uint64_t now_ns,uint64_t heartbeat_timeout_ns);
