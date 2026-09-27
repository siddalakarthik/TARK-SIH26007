#include "command_payload.h"
#include "tark_protocol.h"
#include <float.h>
#include <math.h>
#include <string.h>
_Static_assert(sizeof(float)==4&&sizeof(double)==8&&FLT_RADIX==2&&FLT_MANT_DIG==24&&DBL_MANT_DIG==53,"Protocol V2 requires IEEE binary32/binary64");

typedef struct { const uint8_t *p,*end; } reader_t;
typedef struct { char key[32],text[128]; uint8_t type; uint64_t integer; double number; } value_t;
typedef struct { value_t values[24]; size_t count; } map_t;

static bool head(reader_t *r,uint8_t *major,uint64_t *value,uint8_t *additional) {
    if(r->p>=r->end)return false;
    uint8_t b=*r->p++,a=b&31;*major=b>>5;*additional=a;
    if(a<24){*value=a;return true;}
    size_t n=a==24?1:a==25?2:a==26?4:a==27?8:0;
    if(!n||(size_t)(r->end-r->p)<n)return false;
    uint64_t x=0;for(size_t i=0;i<n;i++)x=(x<<8)|*r->p++;
    if(*major!=7&&((n==1&&x<24)||(n==2&&x<=UINT8_MAX)||(n==4&&x<=UINT16_MAX)||(n==8&&x<=UINT32_MAX)))return false;
    *value=x;return true;
}
static bool read_text(reader_t *r,uint64_t n,char *out,size_t cap) {
    if(!n||n>=cap||(size_t)(r->end-r->p)<n)return false;
    for(size_t i=0;i<(size_t)n;i++){uint8_t c=*r->p++;if(c<32||c>126)return false;out[i]=(char)c;}
    out[n]=0;return true;
}
static bool half_exact(double x) {
    double a=fabs(x);if(a==0)return true;if(a>65504)return false;
    int exp;frexp(a,&exp);
    double scaled=ldexp(a,exp<=-14?24:11-exp);
    return isfinite(scaled)&&scaled==floor(scaled);
}
static double half_value(uint16_t h) {
    int exponent=(h>>10)&31;unsigned fraction=h&1023;
    double x=exponent==0?ldexp((double)fraction,-24):ldexp(1.0+(double)fraction/1024.0,exponent-15);
    return h&0x8000?-x:x;
}
static bool parse(const uint8_t *data,size_t length,map_t *map) {
    if(!data||length>TARK_MAX_PAYLOAD)return false;
    reader_t r={data,data+length};uint8_t major,a;uint64_t count;
    if(!head(&r,&major,&count,&a)||major!=5||count>24)return false;
    map->count=(size_t)count;
    const uint8_t *previous=NULL;size_t previous_n=0;
    for(size_t i=0;i<map->count;i++){
        value_t *v=&map->values[i];memset(v,0,sizeof(*v));
        const uint8_t *key=r.p;uint64_t n;
        if(!head(&r,&major,&n,&a)||major!=3||!read_text(&r,n,v->key,sizeof(v->key)))return false;
        size_t key_n=(size_t)(r.p-key);
        if(previous&&(key_n<previous_n||(key_n==previous_n&&memcmp(previous,key,key_n)>=0)))return false;
        previous=key;previous_n=key_n;
        if(!head(&r,&major,&n,&a))return false;
        v->type=major;v->integer=n;
        if(major==0)v->number=(double)n;
        else if(major==1)v->number=-1.0-(double)n;
        else if(major==3){if(!read_text(&r,n,v->text,sizeof(v->text)))return false;}
        else if(major==7){
            if(a==20||a==21||a==22)continue;
            if(a==25){if(((n>>10)&31)==31)return false;v->number=half_value((uint16_t)n);}
            else if(a==26){uint32_t bits=(uint32_t)n;float x;memcpy(&x,&bits,sizeof(x));v->number=x;if(!isfinite(x)||half_exact(x))return false;}
            else if(a==27){double x;memcpy(&x,&n,sizeof(x));v->number=x;if(!isfinite(x)||(fabs(x)<=FLT_MAX&&(double)(float)x==x))return false;}
            else return false;
            v->type=8; /* finite float, distinct from boolean/null */
        }else return false; /* no nesting, tags, bytes or indefinite forms */
    }
    return r.p==r.end;
}
static const value_t *get(const map_t *m,const char *key) {
    for(size_t i=0;i<m->count;i++)if(!strcmp(m->values[i].key,key))return &m->values[i];
    return NULL;
}
static bool integer(const map_t *m,const char *key,uint64_t *out) {
    const value_t *v=get(m,key);if(!v||v->type!=0)return false;*out=v->integer;return true;
}
static bool numeric(const map_t *m,const char *key,double *out) {
    const value_t *v=get(m,key);if(!v||(v->type!=0&&v->type!=1&&v->type!=8))return false;
    if(v->type==0){uint64_t x=v->integer;unsigned shift=0;while(x>9007199254740992ull){x>>=1;shift++;}if(shift&&(v->integer&((1ull<<shift)-1)))return false;}
    *out=v->number;return isfinite(*out);
}
static const char *text(const map_t *m,const char *key) {
    const value_t *v=get(m,key);return v&&v->type==3?v->text:NULL;
}
static bool equals(const map_t *m,const char *key,const char *expected) {
    const char *value=text(m,key);return value&&expected&&!strcmp(value,expected);
}
static bool hex(const char *s,size_t length) {
    if(!s||strlen(s)!=length)return false;
    for(size_t i=0;i<length;i++)if(!((s[i]>='0'&&s[i]<='9')||(s[i]>='a'&&s[i]<='f')))return false;
    return true;
}
bool tark_canonical_map(const uint8_t *data,size_t length){map_t m;return parse(data,length,&m);}
bool tark_validate_command_cbor(const uint8_t *data,size_t length,uint64_t sequence,uint64_t timestamp,uint64_t now,const char *hash,const char *session,tark_command_payload_t *out) {
    if(!out)return false;
    memset(out,0,sizeof(*out));out->reason="INVALID_PAYLOAD";
    map_t m;uint64_t x;
    if(!parse(data,length,&m)||m.count<12||m.count>13||sequence>UINT32_MAX)return false;
    static const char *keys[]={"protocol_version","sequence","timestamp_ns","valid_until_ns","state","permitted_speed_mps","left_command","right_command","heartbeat","reason_code","configuration_hash","session_id","checksum"};
    for(size_t i=0;i<12;i++)if(!get(&m,keys[i]))return false;
    for(size_t i=0;i<m.count;i++){
        bool known=false;for(size_t j=0;j<13;j++)if(!strcmp(m.values[i].key,keys[j]))known=true;
        if(!known)return false;
    }
    if(!integer(&m,"sequence",&x)||x!=sequence||!integer(&m,"timestamp_ns",&x)||x!=timestamp)return false;
    if(!integer(&m,"protocol_version",&x)||x!=TARK_PROTOCOL_VERSION){out->reason="INVALID_VERSION";return false;}
    if(!text(&m,"configuration_hash"))return false;
    if(!equals(&m,"configuration_hash",hash)){out->reason="CONFIGURATION_MISMATCH";return false;}
    if(!hex(text(&m,"session_id"),48)||!equals(&m,"session_id",session)){out->reason="SESSION_MISMATCH";return false;}
    if(!integer(&m,"valid_until_ns",&out->valid_until_ns)||out->valid_until_ns<=timestamp){out->reason="COMMAND_EXPIRED";return false;}
    uint64_t ttl=out->valid_until_ns-timestamp;
    if(ttl>TARK_MAX_COMMAND_LIFETIME_NS||now>UINT64_MAX-ttl){out->reason="INVALID_LIFETIME";return false;}
    out->local_expiry_ns=now+ttl;
    const char *state=text(&m,"state"),*reason=text(&m,"reason_code");
    if(!state||(strcmp(state,"NORMAL")&&strcmp(state,"WARN")&&strcmp(state,"RESTRICT")&&strcmp(state,"UNKNOWN")&&strcmp(state,"STOP"))||!reason||strlen(reason)>31)return false;
    if(!integer(&m,"heartbeat",&x)||x>UINT32_MAX)return false;
    out->heartbeat=(uint32_t)x;
    if(!numeric(&m,"permitted_speed_mps",&out->permitted_speed_mps)||out->permitted_speed_mps<0||!numeric(&m,"left_command",&out->left_command)||fabs(out->left_command)>1||!numeric(&m,"right_command",&out->right_command)||fabs(out->right_command)>1)return false;
    const value_t *checksum=get(&m,"checksum");if(checksum&&(checksum->type!=7||checksum->integer!=22))return false;
    out->valid=true;out->reason="NONE";return true;
}
bool tark_validate_heartbeat_cbor(const uint8_t *data,size_t length,const char *hash,const char *session) {
    map_t m;uint64_t v;
    return parse(data,length,&m)&&m.count==3&&integer(&m,"protocol_version",&v)&&v==TARK_PROTOCOL_VERSION&&equals(&m,"configuration_hash",hash)&&equals(&m,"session_id",session)&&hex(session,48);
}
bool tark_session_request_cbor(const uint8_t *data,size_t length,const char *hash,char request[33]) {
    map_t m;if(!parse(data,length,&m)||m.count!=2||!equals(&m,"configuration_hash",hash)||!hex(text(&m,"request_id"),32))return false;
    memcpy(request,text(&m,"request_id"),33);return true;
}
