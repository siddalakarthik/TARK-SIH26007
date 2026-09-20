#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "tark_protocol.h"

/* All response builders are bounded/static and Phase-1 output is always zero. */
bool tark_build_ack(uint64_t sequence,uint64_t timestamp_ns,const char *reason,uint8_t *out,size_t *out_size);
bool tark_build_nack(uint64_t sequence,uint64_t timestamp_ns,const char *reason,uint8_t *out,size_t *out_size);
bool tark_build_status(uint64_t sequence,uint64_t timestamp_ns,const char *reason,uint8_t *out,size_t *out_size);
