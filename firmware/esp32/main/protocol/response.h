#pragma once
#include "tark_protocol.h"
bool tark_build_ack(uint64_t sequence,uint64_t timestamp,const char *reason,const char *hash,const char *session,uint8_t *out,size_t *out_n);
bool tark_build_nack(uint64_t sequence,uint64_t timestamp,const char *reason,const char *hash,const char *session,uint8_t *out,size_t *out_n);
bool tark_build_status(uint64_t sequence,uint64_t timestamp,const char *reason,const char *hash,const char *session,uint8_t *out,size_t *out_n);
bool tark_build_session(uint64_t timestamp,const char *request,const char *hash,const char *session,uint8_t *out,size_t *out_n);
