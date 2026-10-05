/* Pure host fixture. No hardware APIs; same production response encoder. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../main/protocol/response.h"
#include "../main/protocol/command_payload.h"
#include "r3_protocol_vectors.h"

int main(void){
    tark_encoder_observation_t s={0};
    s.node_id="A";s.source_id="encoders-a";
    s.session_id="111111111111111111111111111111110000000000000001";
    s.configuration_hash="x";s.left_count=-42;s.right_count=43;s.invalid_edges=2;
    s.source_counter=1;s.interval_start_ns=998000;s.interval_end_ns=999000;
    for(size_t i=0;i<sizeof(SHARED_VECTORS)/sizeof(SHARED_VECTORS[0]);i++){
        uint32_t sequence=1;
        if(i==1){sequence=UINT32_MAX;s.left_count=INT32_MIN;s.right_count=INT32_MAX;
            s.drop_count=UINT32_MAX;s.source_counter=UINT32_MAX;s.lost_edges_known=true;s.calibration_id="encoder-fixture:1";}
        uint8_t out[TARK_MAX_FRAME],scratch[TARK_MAX_FRAME];size_t n=sizeof(out);tark_frame_t decoded;
        assert(tark_build_encoder_observation(sequence,1000000,&s,out,&n));
        assert(n==SHARED_VECTORS[i].size&&!memcmp(out,SHARED_VECTORS[i].frame,n));
        assert(tark_decode_frame(out,n,scratch,sizeof(scratch),&decoded)==TARK_OK);
        assert(decoded.type==TARK_OBSERVATION&&tark_canonical_map(decoded.payload,decoded.payload_length));
        printf("FRAME ");for(size_t j=0;j<n;j++)printf("%02x",out[j]);puts("");
    }
    uint8_t out[TARK_MAX_FRAME];size_t n=sizeof(out);
    s.interval_start_ns=s.interval_end_ns;assert(!tark_build_encoder_observation(1,1000000,&s,out,&n));
    s.interval_start_ns=1;s.session_id="not-a-session";assert(!tark_build_encoder_observation(1,1000000,&s,out,&n));
    puts("R3 observation encoder/shared vectors PASS");return 0;
}
