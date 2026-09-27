/* Host-only stdin/stdout harness. No device or platform APIs. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../main/protocol/service.h"
#include "../main/protocol/command_payload.h"
static void tx(const uint8_t *f,size_t n,void *ctx){(void)ctx;printf("FRAME ");for(size_t i=0;i<n;i++)printf("%02x",f[i]);puts("");}
static size_t unhex(const char *s,uint8_t *out){size_t len=strlen(s);if(len%2||len/2>TARK_MAX_FRAME)return 0;for(size_t i=0;i<len/2;i++){char b[3]={s[i*2],s[i*2+1],0};char *end;unsigned long x=strtoul(b,&end,16);if(*end)return 0;out[i]=(uint8_t)x;}return len/2;}
int main(void){
    tark_protocol_service_t s;tark_protocol_service_init(&s,"x","11111111111111111111111111111111",tx,NULL);
    char line[2048],op[32],hex[1281];unsigned long long now;
    while(fgets(line,sizeof(line),stdin)){
        hex[0]=0;if(sscanf(line,"%31s %llu %1280s",op,&now,hex)<2)return 2;
        uint8_t bytes[TARK_MAX_FRAME];size_t n=unhex(hex,bytes);
        if(!strcmp(op,"RX"))tark_protocol_service_receive(&s,bytes,n,(uint64_t)now);
        else if(!strcmp(op,"TICK"))tark_protocol_service_tick(&s,(uint64_t)now);
        else if(!strcmp(op,"DISCONNECT"))tark_protocol_service_disconnect(&s);
        else if(!strcmp(op,"BOOT"))tark_protocol_service_init(&s,"x",hex,tx,NULL);
        else if(!strcmp(op,"CHECK")){
            uint8_t scratch[TARK_MAX_FRAME];tark_frame_t f;tark_command_payload_t c;
            if(tark_decode_frame(bytes,n,scratch,sizeof(scratch),&f)!=TARK_OK){puts("CHECK REJECT FRAME");continue;}
            if(!tark_canonical_map(f.payload,f.payload_length)){puts("CHECK REJECT CBOR");continue;}
            if(f.type==TARK_COMMAND){
                if(!tark_validate_command_cbor(f.payload,f.payload_length,f.sequence,f.timestamp_ns,(uint64_t)now,"x","111111111111111111111111111111110000000000000001",&c))printf("CHECK REJECT %s\n",c.reason);
                else printf("CHECK OK %llu %.17g %.17g %.17g\n",(unsigned long long)c.local_expiry_ns,c.permitted_speed_mps,c.left_command,c.right_command);
            }else puts("CHECK OK");
            continue;
        }else return 3;
        printf("STATE %d %llu %u %d %s\n",s.supervisor.active,(unsigned long long)s.supervisor.local_expiry_ns,s.supervisor.last_sequence,s.supervisor.phase1_output_disabled,s.supervisor.last_rejection);
    }
    return 0;
}
