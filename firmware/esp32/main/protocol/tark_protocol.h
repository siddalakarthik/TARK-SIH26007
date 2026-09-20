#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define TARK_MAGIC 0x544Bu
#define TARK_PROTOCOL_VERSION 1u
#define TARK_MAX_PAYLOAD 512u
#define TARK_MAX_FRAME 640u
typedef enum { TARK_COMMAND=1, TARK_ACK=2, TARK_NACK=3, TARK_HEARTBEAT=4, TARK_STATUS=5 } tark_message_type_t;
typedef enum { TARK_OK=0, TARK_BAD_MAGIC, TARK_BAD_LENGTH, TARK_BAD_FRAME, TARK_BAD_CRC, TARK_BAD_VERSION, TARK_OVERSIZED, TARK_UNKNOWN_TYPE } tark_protocol_result_t;
/* The v1 wire envelope uses uint64 big-endian sequence and timestamp fields.
 * COMMAND semantics separately reject sequence values above UINT32_MAX. */
typedef struct { uint8_t type; uint64_t sequence; uint64_t timestamp_ns; uint32_t payload_length; const uint8_t *payload; } tark_frame_t;
uint32_t tark_crc32c(const uint8_t *data, size_t size);
tark_protocol_result_t tark_cobs_decode(const uint8_t *in, size_t in_len, uint8_t *out, size_t *out_len);
tark_protocol_result_t tark_cobs_encode(const uint8_t *in, size_t in_len, uint8_t *out, size_t *out_len);
tark_protocol_result_t tark_decode_frame(const uint8_t *frame, size_t frame_len, uint8_t *scratch, size_t scratch_size, tark_frame_t *out);
