#pragma once
#include <stddef.h>
#include <stdint.h>
#include "tark_protocol.h"
#include "response.h"
#include "../command/command_supervisor.h"

typedef void (*tark_tx_callback_t)(const uint8_t *frame,size_t length,void *context);
typedef struct {uint8_t encoded[TARK_MAX_FRAME];size_t encoded_length;bool in_frame;command_supervisor_t supervisor;const char *configuration_hash;tark_tx_callback_t tx;void *tx_context;uint32_t frames_valid;uint32_t frames_invalid;char boot_id[33],session_id[49];uint64_t generation,last_status_ns,last_tick_ns;bool available,session_active,tick_seen;} tark_protocol_service_t;
/* boot_id: unique 128-bit lowercase hex per boot, supplied by a reviewed
 * platform binding. NULL keeps the endpoint unavailable, not fake-verified. */
void tark_protocol_service_init(tark_protocol_service_t *service,const char *configuration_hash,const char *boot_id,tark_tx_callback_t tx,void *tx_context);
/* Feed an arbitrary serial byte chunk. It is nonblocking, bounded and recovers
 * at the next delimiter after a malformed/oversize frame. */
void tark_protocol_service_receive(tark_protocol_service_t *service,const uint8_t *bytes,size_t length,uint64_t now_ns);
void tark_protocol_service_status(tark_protocol_service_t *service,uint64_t sequence,uint64_t now_ns);
void tark_protocol_service_tick(tark_protocol_service_t *service,uint64_t now_ns);
void tark_protocol_service_disconnect(tark_protocol_service_t *service);
/* Observation-only emission. Caller supplies source sequence; no motor output.
 * The active service supplies configuration/session, not untrusted sensor data. */
bool tark_protocol_service_encoder(tark_protocol_service_t *service,uint32_t sequence,uint64_t now_ns,const tark_encoder_observation_t *sample);
