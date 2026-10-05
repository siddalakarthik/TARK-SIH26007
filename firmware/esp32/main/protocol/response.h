#pragma once
#include "tark_protocol.h"
bool tark_build_ack(uint64_t sequence,uint64_t timestamp,const char *reason,const char *hash,const char *session,uint8_t *out,size_t *out_n);
bool tark_build_nack(uint64_t sequence,uint64_t timestamp,const char *reason,const char *hash,const char *session,uint8_t *out,size_t *out_n);
bool tark_build_status(uint64_t sequence,uint64_t timestamp,const char *reason,const char *hash,const char *session,uint8_t *out,size_t *out_n);
bool tark_build_session(uint64_t timestamp,const char *request,const char *hash,const char *session,uint8_t *out,size_t *out_n);
/* Observation-only extension of the existing V2 envelope. No GPIO access. */
typedef struct {
    const char *node_id, *source_id, *session_id, *configuration_hash, *calibration_id;
    int32_t left_count, right_count;
    uint32_t drop_count, fault_bits, invalid_edges, source_counter, lost_edges;
    bool lost_edges_known;
    uint64_t interval_start_ns, interval_end_ns;
} tark_encoder_observation_t;
bool tark_build_encoder_observation(uint32_t sequence,uint64_t timestamp,const tark_encoder_observation_t *sample,uint8_t *out,size_t *out_n);
