#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../main/protocol/tark_protocol.h"
#include "../main/protocol/command_payload.h"
#include "../main/command/command_supervisor.h"
#include "../main/hardware/motor_driver.h"
#include "../main/safety/watchdog.h"
#include "protocol_vectors.h"
int main(void){
    assert(tark_crc32c((const uint8_t*)"123456789",9)==0xe3069283u);
    for(size_t i=0;i<sizeof(SHARED_VECTORS)/sizeof(SHARED_VECTORS[0]);i++){
        const shared_vector_t *v=&SHARED_VECTORS[i];uint8_t scratch[640],encoded[640];tark_frame_t f;
        tark_protocol_result_t decoded=tark_decode_frame(v->frame,v->size,scratch,sizeof(scratch),&f);
        if(!v->frame_valid){assert(decoded!=TARK_OK);continue;}
        assert(decoded==TARK_OK);
        assert(tark_canonical_map(f.payload,f.payload_length)==(v->canonical!=0));
        size_t dn=sizeof(scratch);assert(tark_cobs_decode(v->frame+1,v->size-2,scratch,&dn)==TARK_OK);
        size_t en=sizeof(encoded);assert(tark_cobs_encode(scratch,dn,encoded,&en)==TARK_OK);
        assert(en==v->size-2&&!memcmp(encoded,v->frame+1,en));
        if(f.type==TARK_COMMAND){
            tark_command_payload_t command;
            bool ok=tark_validate_command_cbor(f.payload,f.payload_length,f.sequence,f.timestamp_ns,12000000000ull,"x","111111111111111111111111111111110000000000000001",&command);
            if(ok!=(v->command_valid!=0))printf("vector failed: %s\n",v->name);
            assert(ok==(v->command_valid!=0));
            if(ok){assert(command.permitted_speed_mps==v->speed&&command.left_command==v->left&&command.right_command==v->right);assert(command.local_expiry_ns==12000000000ull+v->until-f.timestamp_ns);}
            else if(v->canonical)assert(!strcmp(command.reason,v->reason));
        }
    }
    uint8_t buffer[4];size_t n=sizeof(buffer);assert(tark_cobs_decode((const uint8_t[]){2},1,buffer,&n)==TARK_BAD_FRAME);
    n=sizeof(buffer);assert(tark_cobs_decode((const uint8_t[]){1,1,2,1},4,buffer,&n)==TARK_OK);
    assert(n==3&&!memcmp(buffer,(const uint8_t[]){0,0,1},3));
    n=sizeof(buffer);assert(tark_cobs_decode((const uint8_t[]){1,1,2,1,1},5,buffer,&n)==TARK_OK);
    assert(n==4&&!memcmp(buffer,(const uint8_t[]){0,0,1,0},4));
    n=sizeof(buffer);assert(tark_cobs_decode((const uint8_t[]){2,0},2,buffer,&n)==TARK_BAD_FRAME);
    tark_command_payload_t mismatched;
    assert(!tark_validate_command_cbor(VECTOR_COMMAND_CBOR,VECTOR_COMMAND_CBOR_SIZE,2,1000000000ull,12000000000ull,"x","111111111111111111111111111111110000000000000001",&mismatched));
    command_supervisor_t supervisor;command_supervisor_init(&supervisor);
    assert(command_supervisor_accept(&supervisor,UINT32_MAX,100,200,true)==NACK_NONE);
    assert(command_supervisor_accept(&supervisor,0,101,200,true)==NACK_OLD_SEQUENCE);
    command_supervisor_init(&supervisor);assert(command_supervisor_accept(&supervisor,1,100,200,true)==NACK_NONE);
    assert(command_supervisor_accept(&supervisor,1,101,200,true)==NACK_DUPLICATE_SEQUENCE);
    assert(command_supervisor_accept(&supervisor,2,201,200,true)==NACK_EXPIRED_COMMAND);
    command_supervisor_init(&supervisor);assert(command_supervisor_accept(&supervisor,1,100,200,true)==NACK_NONE);
    command_supervisor_tick(&supervisor,200,500);assert(!supervisor.active&&supervisor.phase1_output_disabled);
    motor_driver_t motor;motor_driver_init(&motor);assert(!motor_driver_apply_bounded(&motor,2,-2));assert(motor.applied_left==0&&motor.applied_right==0);
    tark_watchdog_t watchdog;tark_watchdog_init(&watchdog,100);assert(tark_watchdog_expired(&watchdog,701,500));
    puts("host protocol/shared semantic vectors PASS");return 0;
}
