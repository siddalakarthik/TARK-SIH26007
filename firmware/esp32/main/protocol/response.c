#include "response.h"
#include <string.h>

typedef struct {uint8_t *p,*end;bool ok;} writer_t;
static void byte(writer_t *w,uint8_t x){if(w->p>=w->end){w->ok=false;return;}*w->p++=x;}
static void text(writer_t *w,const char *s){if(!s){w->ok=false;return;}size_t n=strlen(s);if(!n||n>127){w->ok=false;return;}if(n>23){byte(w,0x78);byte(w,(uint8_t)n);}else byte(w,(uint8_t)(0x60+n));for(size_t i=0;i<n;i++)byte(w,(uint8_t)s[i]);}
static void fzero(writer_t *w){byte(w,0xf9);byte(w,0);byte(w,0);}
static bool frame(uint8_t type,uint64_t seq,uint64_t ts,const uint8_t *payload,size_t pn,uint8_t *out,size_t *on){
    uint8_t raw[TARK_MAX_FRAME];if(!out||!on||pn>TARK_MAX_PAYLOAD||*on<TARK_MAX_FRAME||seq>UINT32_MAX)return false;
    raw[0]=0x54;raw[1]=0x4b;raw[2]=TARK_PROTOCOL_VERSION;raw[3]=type;
    for(int i=0;i<4;i++)raw[4+i]=(uint8_t)(pn>>(24-8*i));
    for(int i=0;i<8;i++){raw[8+i]=(uint8_t)(seq>>(56-8*i));raw[16+i]=(uint8_t)(ts>>(56-8*i));}
    memcpy(raw+24,payload,pn);uint32_t crc=tark_crc32c(raw,24+pn);
    for(int i=0;i<4;i++)raw[24+pn+i]=(uint8_t)(crc>>(24-8*i));
    size_t n=*on-2;if(tark_cobs_encode(raw,28+pn,out+1,&n)!=TARK_OK||n+2>*on)return false;
    out[0]=0;out[n+1]=0;*on=n+2;return true;
}
static void identity(writer_t *w,const char *session){text(w,"session_id");text(w,session);text(w,"source_mode");text(w,"REAL");}
static bool response(uint8_t type,uint64_t seq,uint64_t ts,const char *reason,const char *hash,const char *session,uint8_t *out,size_t *on){
    uint8_t payload[TARK_MAX_PAYLOAD];writer_t w={payload,payload+sizeof(payload),true};byte(&w,0xa8);
    text(&w,"reason");text(&w,reason);text(&w,"accepted");byte(&w,type==TARK_ACK?0xf5:0xf4);identity(&w,session);
    text(&w,"applied_left");fzero(&w);text(&w,"output_state");text(&w,"DISABLED_PHASE_1");text(&w,"applied_right");fzero(&w);text(&w,"configuration_hash");text(&w,hash);
    return w.ok&&frame(type,seq,ts,payload,(size_t)(w.p-payload),out,on);
}
bool tark_build_ack(uint64_t q,uint64_t t,const char *r,const char *h,const char *s,uint8_t *o,size_t *n){return response(TARK_ACK,q,t,r,h,s,o,n);}
bool tark_build_nack(uint64_t q,uint64_t t,const char *r,const char *h,const char *s,uint8_t *o,size_t *n){return response(TARK_NACK,q,t,r,h,s,o,n);}
bool tark_build_status(uint64_t q,uint64_t t,const char *r,const char *h,const char *s,uint8_t *o,size_t *n){
    uint8_t p[TARK_MAX_PAYLOAD];writer_t w={p,p+sizeof(p),true};byte(&w,0xa5);text(&w,"reason");text(&w,r);identity(&w,s);
    text(&w,"output_state");text(&w,"DISABLED_PHASE_1");text(&w,"configuration_hash");text(&w,h);
    return w.ok&&frame(TARK_STATUS,q,t,p,(size_t)(w.p-p),o,n);
}
bool tark_build_session(uint64_t t,const char *request,const char *h,const char *s,uint8_t *o,size_t *n){
    uint8_t p[TARK_MAX_PAYLOAD];writer_t w={p,p+sizeof(p),true};byte(&w,0xa4);text(&w,"request_id");text(&w,request);identity(&w,s);
    text(&w,"configuration_hash");text(&w,h);return w.ok&&frame(TARK_SESSION_READY,0,t,p,(size_t)(w.p-p),o,n);
}

/* Canonical integers share the existing response writer and frame/CRC/COBS path. */
static void unsigned_value(writer_t *w,uint8_t major,uint64_t value){
    if(value<24){byte(w,(uint8_t)(major|value));return;}
    unsigned int width=value<=UINT8_MAX?1:value<=UINT16_MAX?2:value<=UINT32_MAX?4:8;
    byte(w,(uint8_t)(major|(width==1?24:width==2?25:width==4?26:27)));
    for(unsigned int i=width;i>0;i--)byte(w,(uint8_t)(value>>(8*(i-1))));
}
static void integer(writer_t *w,int32_t value){
    if(value>=0)unsigned_value(w,0,(uint32_t)value);
    else unsigned_value(w,0x20,(uint64_t)(-(int64_t)value-1));
}
static bool limited_text(const char *s,size_t maximum){
    if(!s)return false;
    size_t n=strlen(s);if(n==0||n>maximum)return false;
    for(size_t i=0;i<n;i++)if((unsigned char)s[i]<32||(unsigned char)s[i]>126)return false;
    return true;
}
bool tark_build_encoder_observation(uint32_t q,uint64_t ts,const tark_encoder_observation_t *s,uint8_t *out,size_t *out_n){
    if(!s||!limited_text(s->node_id,16)||!limited_text(s->source_id,32)||!limited_text(s->configuration_hash,64)||
       !limited_text(s->session_id,48)||strlen(s->session_id)!=48||
       (s->calibration_id&&!limited_text(s->calibration_id,64))||
       s->interval_start_ns>=s->interval_end_ns||s->interval_end_ns>ts)return false;
    for(size_t i=0;i<48;i++)if(!((s->session_id[i]>='0'&&s->session_id[i]<='9')||(s->session_id[i]>='a'&&s->session_id[i]<='f')))return false;
    uint8_t payload[TARK_MAX_PAYLOAD];writer_t w={payload,payload+sizeof(payload),true};byte(&w,0xb0);
    text(&w,"kind");text(&w,"ENCODER_V1");
    text(&w,"node_id");text(&w,s->node_id);
    text(&w,"source_id");text(&w,s->source_id);
    text(&w,"drop_count");unsigned_value(&w,0,s->drop_count);
    text(&w,"fault_bits");unsigned_value(&w,0,s->fault_bits);
    text(&w,"left_count");integer(&w,s->left_count);
    text(&w,"lost_edges");if(s->lost_edges_known)unsigned_value(&w,0,s->lost_edges);else byte(&w,0xf6);
    text(&w,"session_id");text(&w,s->session_id);
    text(&w,"right_count");integer(&w,s->right_count);
    text(&w,"source_mode");text(&w,"REAL");
    text(&w,"invalid_edges");unsigned_value(&w,0,s->invalid_edges);
    text(&w,"calibration_id");if(s->calibration_id)text(&w,s->calibration_id);else byte(&w,0xf6);
    text(&w,"source_counter");unsigned_value(&w,0,s->source_counter);
    text(&w,"interval_end_ns");unsigned_value(&w,0,s->interval_end_ns);
    text(&w,"interval_start_ns");unsigned_value(&w,0,s->interval_start_ns);
    text(&w,"configuration_hash");text(&w,s->configuration_hash);
    return w.ok&&frame(TARK_OBSERVATION,q,ts,payload,(size_t)(w.p-payload),out,out_n);
}
