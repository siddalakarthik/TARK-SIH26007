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
