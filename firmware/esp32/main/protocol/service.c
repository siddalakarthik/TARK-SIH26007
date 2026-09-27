#include "service.h"
#include "command_payload.h"
#include "response.h"
#include <string.h>

static void reject(tark_protocol_service_t *s,const char *reason){s->frames_invalid++;s->supervisor.active=false;s->supervisor.phase1_output_disabled=true;s->supervisor.last_rejection=reason;}
static void send_response(tark_protocol_service_t *s,bool ok,uint64_t q,uint64_t ts,const char *reason){
    uint8_t out[TARK_MAX_FRAME];size_t n=sizeof(out);
    if((ok?tark_build_ack(q,ts,reason,s->configuration_hash,s->session_id,out,&n):tark_build_nack(q,ts,reason,s->configuration_hash,s->session_id,out,&n))&&s->tx)s->tx(out,n,s->tx_context);
}
static void process(tark_protocol_service_t *s,uint64_t now){
    uint8_t framed[TARK_MAX_FRAME],scratch[TARK_MAX_FRAME];tark_frame_t f;
    if(s->encoded_length+2>TARK_MAX_FRAME){reject(s,"INVALID_LENGTH");return;}
    framed[0]=0;memcpy(framed+1,s->encoded,s->encoded_length);framed[s->encoded_length+1]=0;
    if(tark_decode_frame(framed,s->encoded_length+2,scratch,sizeof(scratch),&f)!=TARK_OK){reject(s,"INVALID_PAYLOAD");return;}
    if(!s->available){reject(s,"NOT_ENABLED");return;}
    if(f.type==TARK_SESSION_OPEN){
        char request[33];
        if(f.sequence!=0||!tark_session_request_cbor(f.payload,f.payload_length,s->configuration_hash,request)||s->generation==UINT64_MAX){reject(s,"INVALID_PAYLOAD");return;}
        s->generation++;memcpy(s->session_id,s->boot_id,32);
        static const char hex[]="0123456789abcdef";
        for(int i=0;i<16;i++)s->session_id[32+i]=hex[(s->generation>>(60-4*i))&15];
        s->session_id[48]=0;s->session_active=true;command_supervisor_init(&s->supervisor);s->last_status_ns=now;
        uint8_t out[TARK_MAX_FRAME];size_t n=sizeof(out);
        if(tark_build_session(f.timestamp_ns,request,s->configuration_hash,s->session_id,out,&n)&&s->tx)s->tx(out,n,s->tx_context);
        s->frames_valid++;return;
    }
    if(!s->session_active){reject(s,"SESSION_MISMATCH");return;}
    if(f.type==TARK_COMMAND){
        tark_command_payload_t command;
        if(!tark_validate_command_cbor(f.payload,f.payload_length,f.sequence,f.timestamp_ns,now,s->configuration_hash,s->session_id,&command)){
            reject(s,command.reason);send_response(s,false,f.sequence,f.timestamp_ns,command.reason);return;
        }
        command_reject_t failure=command_supervisor_accept(&s->supervisor,(uint32_t)f.sequence,now,command.local_expiry_ns,true);
        if(failure!=NACK_NONE){s->frames_invalid++;send_response(s,false,f.sequence,f.timestamp_ns,s->supervisor.last_rejection);return;}
        s->frames_valid++;send_response(s,true,f.sequence,f.timestamp_ns,"COMMAND_ACCEPTED_DISABLED_PHASE_1");return;
    }
    if(f.type==TARK_HEARTBEAT){
        if(!tark_validate_heartbeat_cbor(f.payload,f.payload_length,s->configuration_hash,s->session_id)){
            reject(s,"INVALID_PAYLOAD");send_response(s,false,f.sequence,f.timestamp_ns,"INVALID_PAYLOAD");return;
        }
        if(s->supervisor.seen&&f.sequence<=s->supervisor.last_sequence){reject(s,"OLD_SEQUENCE");send_response(s,false,f.sequence,f.timestamp_ns,"OLD_SEQUENCE");return;}
        s->supervisor.seen=true;s->supervisor.last_sequence=(uint32_t)f.sequence;s->supervisor.heartbeat_ns=now;
        /* Heartbeat never extends a command deadline or reactivates expiry. */
        s->frames_valid++;send_response(s,true,f.sequence,f.timestamp_ns,"HEARTBEAT_ACCEPTED");return;
    }
    reject(s,"UNEXPECTED_MESSAGE");send_response(s,false,f.sequence,f.timestamp_ns,"UNEXPECTED_MESSAGE");
}
void tark_protocol_service_init(tark_protocol_service_t *s,const char *hash,const char *boot,tark_tx_callback_t tx,void *context){
    memset(s,0,sizeof(*s));command_supervisor_init(&s->supervisor);s->configuration_hash=hash;s->tx=tx;s->tx_context=context;
    if(!hash||!boot||strlen(boot)!=32)return;
    for(size_t i=0;i<32;i++)if(!((boot[i]>='0'&&boot[i]<='9')||(boot[i]>='a'&&boot[i]<='f')))return;
    memcpy(s->boot_id,boot,33);s->available=true;
}
void tark_protocol_service_disconnect(tark_protocol_service_t *s){
    s->encoded_length=0;s->in_frame=false;s->session_active=false;s->session_id[0]=0;
    command_supervisor_force_safe_stop(&s->supervisor,NACK_NOT_ENABLED);
}
void tark_protocol_service_receive(tark_protocol_service_t *s,const uint8_t *bytes,size_t length,uint64_t now){
    if(!s||(!bytes&&length))return;
    if(s->tick_seen&&now<s->last_tick_ns){reject(s,"INTERNAL_FAULT");return;}
    s->tick_seen=true;s->last_tick_ns=now;
    command_supervisor_tick(&s->supervisor,now,TARK_MAX_COMMAND_LIFETIME_NS);
    for(size_t i=0;i<length;i++){
        uint8_t b=bytes[i];
        if(b==0){if(s->in_frame&&s->encoded_length)process(s,now);s->encoded_length=0;s->in_frame=true;continue;}
        if(!s->in_frame)continue;
        if(s->encoded_length>=TARK_MAX_FRAME-2){s->encoded_length=0;s->in_frame=false;reject(s,"INVALID_LENGTH");continue;}
        s->encoded[s->encoded_length++]=b;
    }
}
void tark_protocol_service_status(tark_protocol_service_t *s,uint64_t q,uint64_t now){
    uint8_t out[TARK_MAX_FRAME];size_t n=sizeof(out);
    if(s&&s->session_active&&tark_build_status(q,now,s->supervisor.last_rejection,s->configuration_hash,s->session_id,out,&n)&&s->tx)s->tx(out,n,s->tx_context);
}
void tark_protocol_service_tick(tark_protocol_service_t *s,uint64_t now){
    if(!s)return;
    if(s->tick_seen&&now<s->last_tick_ns){command_supervisor_force_safe_stop(&s->supervisor,NACK_INTERNAL_FAULT);return;}
    s->last_tick_ns=now;s->tick_seen=true;
    command_supervisor_tick(&s->supervisor,now,TARK_MAX_COMMAND_LIFETIME_NS);
    if(s->session_active&&(now<s->last_status_ns||now-s->last_status_ns>=250000000ull)){
        tark_protocol_service_status(s,s->supervisor.last_sequence,now);s->last_status_ns=now;
    }
}
