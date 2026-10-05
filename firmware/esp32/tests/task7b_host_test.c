#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../main/protocol/response.h"
#include "../main/protocol/service.h"
#include "protocol_vectors.h"
typedef struct {uint8_t frame[TARK_MAX_FRAME];size_t length;unsigned count;} capture_t;
static void capture(const uint8_t *f,size_t n,void *context){capture_t *out=context;assert(n<=sizeof(out->frame));memcpy(out->frame,f,n);out->length=n;out->count++;}
static void equal(const uint8_t *a,size_t an,const uint8_t *b,size_t bn){assert(an==bn&&!memcmp(a,b,an));}
int main(void){
    const char *sid="111111111111111111111111111111110000000000000001";
    uint8_t out[TARK_MAX_FRAME];size_t n=sizeof(out);
    assert(tark_build_ack(1,1000000000ull,"COMMAND_ACCEPTED_DISABLED_PHASE_1","x",sid,out,&n));equal(out,n,VECTOR_ACK_FRAME,VECTOR_ACK_FRAME_SIZE);
    n=sizeof(out);assert(tark_build_nack(2,1000000001ull,"CONFIGURATION_MISMATCH","x",sid,out,&n));equal(out,n,VECTOR_NACK_FRAME,VECTOR_NACK_FRAME_SIZE);
    n=sizeof(out);assert(tark_build_status(42,123456789ull,"NONE","x",sid,out,&n));equal(out,n,VECTOR_STATUS_FRAME,VECTOR_STATUS_FRAME_SIZE);
    capture_t captured={0};tark_protocol_service_t s;
    tark_protocol_service_init(&s,"x",NULL,capture,&captured);
    tark_protocol_service_receive(&s,VECTOR_SESSION_OPEN_FRAME,VECTOR_SESSION_OPEN_FRAME_SIZE,1);assert(captured.count==0&&!s.available);
    tark_protocol_service_init(&s,"x","11111111111111111111111111111111",capture,&captured);
    tark_protocol_service_receive(&s,VECTOR_SESSION_OPEN_FRAME,VECTOR_SESSION_OPEN_FRAME_SIZE,12000000000ull);
    equal(captured.frame,captured.length,VECTOR_SESSION_READY_FRAME,VECTOR_SESSION_READY_FRAME_SIZE);
    tark_protocol_service_receive(&s,VECTOR_COMMAND_FRAME,11,12000000000ull);assert(captured.count==1);
    tark_protocol_service_receive(&s,VECTOR_COMMAND_FRAME+11,VECTOR_COMMAND_FRAME_SIZE-11,12000000000ull);
    equal(captured.frame,captured.length,VECTOR_ACK_FRAME,VECTOR_ACK_FRAME_SIZE);assert(s.supervisor.active&&s.supervisor.local_expiry_ns==12500000000ull);
    tark_protocol_service_tick(&s,12499999999ull);assert(s.supervisor.active);
    tark_protocol_service_tick(&s,12500000000ull);assert(!s.supervisor.active&&!strcmp(s.supervisor.last_rejection,"COMMAND_EXPIRED"));
    assert(s.supervisor.phase1_output_disabled&&captured.count>=3);
    tark_protocol_service_disconnect(&s);assert(!s.session_active);
    unsigned count=captured.count;tark_protocol_service_receive(&s,VECTOR_COMMAND_FRAME,VECTOR_COMMAND_FRAME_SIZE,12600000000ull);assert(captured.count==count);
    tark_protocol_service_receive(&s,VECTOR_SESSION_OPEN_FRAME,VECTOR_SESSION_OPEN_FRAME_SIZE,12600000000ull);assert(s.generation==2);
    tark_protocol_service_receive(&s,VECTOR_COMMAND_FRAME,VECTOR_COMMAND_FRAME_SIZE,12600000000ull);assert(!s.supervisor.active&&!strcmp(s.supervisor.last_rejection,"SESSION_MISMATCH"));
    puts("host session/periodic supervisor PASS");return 0;
}
