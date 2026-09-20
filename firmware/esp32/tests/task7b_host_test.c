#include <assert.h>
#include <string.h>
#include "../main/protocol/response.h"
#include "../main/protocol/service.h"
#include "protocol_vectors.h"

typedef struct {uint8_t frame[TARK_MAX_FRAME];size_t length;unsigned count;} capture_t;
static void capture(const uint8_t *frame,size_t length,void *context){capture_t *out=context;assert(length<=sizeof(out->frame));memcpy(out->frame,frame,length);out->length=length;out->count++;}
static void equals(const uint8_t *actual,size_t actual_n,const uint8_t *expected,size_t expected_n){assert(actual_n==expected_n);assert(!memcmp(actual,expected,actual_n));}
int main(void){uint8_t output[TARK_MAX_FRAME];size_t n=sizeof(output);assert(tark_build_ack(1,1000000000ull,"COMMAND_ACCEPTED_DISABLED_PHASE_1",output,&n));equals(output,n,VECTOR_ACK_FRAME,VECTOR_ACK_FRAME_SIZE);n=sizeof(output);assert(tark_build_nack(2,1000000001ull,"CONFIGURATION_MISMATCH",output,&n));equals(output,n,VECTOR_NACK_FRAME,VECTOR_NACK_FRAME_SIZE);n=sizeof(output);assert(tark_build_status(42,123456789ull,"NONE",output,&n));equals(output,n,VECTOR_STATUS_FRAME,VECTOR_STATUS_FRAME_SIZE);capture_t captured={0};tark_protocol_service_t service;tark_protocol_service_init(&service,"x",capture,&captured);tark_protocol_service_receive(&service,VECTOR_COMMAND_FRAME,11,1000000000ull);assert(captured.count==0);tark_protocol_service_receive(&service,VECTOR_COMMAND_FRAME+11,VECTOR_COMMAND_FRAME_SIZE-11,1000000000ull);assert(captured.count==1);equals(captured.frame,captured.length,VECTOR_ACK_FRAME,VECTOR_ACK_FRAME_SIZE);tark_protocol_service_status(&service,42,123456789ull);assert(captured.count==2);equals(captured.frame,captured.length,VECTOR_STATUS_FRAME,VECTOR_STATUS_FRAME_SIZE);return 0;}
