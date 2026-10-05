"""Generate both-language artifacts from the single reviewed vector inventory."""
from __future__ import annotations
import json
import sys
import struct
from pathlib import Path
ROOT=Path(__file__).parents[1]
def c_bytes(value:str)->str:return ",".join(f"0x{value[i:i+2]}" for i in range(0,len(value),2))
def render_header(vectors:list[dict])->str:
    lines=["/* Generated from protocol_vectors.json; do not edit manually. */","#pragma once","#include <stdint.h>","#include <stddef.h>"]
    for vector in vectors:
        name=vector["name"].upper()
        for field in ("cbor_hex","frame_hex"):
            symbol=f"VECTOR_{name}_{'CBOR' if field=='cbor_hex' else 'FRAME'}"
            lines.append(f"static const uint8_t {symbol}[]={{"+c_bytes(vector[field])+"};")
            lines.append(f"static const size_t {symbol}_SIZE=sizeof({symbol});")
    lines.append('typedef struct { const char *name; const uint8_t *frame; size_t size; int frame_valid,canonical,command_valid; double speed,left,right; uint64_t until; const char *reason; } shared_vector_t;')
    lines.append('static const shared_vector_t SHARED_VECTORS[]={')
    for v in vectors:
        p=v['payload']; name=v['name'].upper()
        lines.append('{'+f'"{v["name"]}",VECTOR_{name}_FRAME,sizeof(VECTOR_{name}_FRAME),{int(v.get("expect_frame_valid",True))},{int(v.get("expect_canonical",True))},{int(v.get("expect_command_valid",True))},'+','.join(str(p.get(k,0)) for k in ('permitted_speed_mps','left_command','right_command'))+f',{p.get("valid_until_ns",0)}ull,"{v.get("reason","NONE")}"'+'},')
    lines.append('};')
    return "\n".join(lines)+"\n"
if __name__=="__main__":
    source_name='r3_protocol_vectors' if '--r3' in sys.argv else 'protocol_vectors'
    vectors=json.loads((ROOT/f'{source_name}.json').read_text())
    if '--refresh' in sys.argv:
        sys.path.insert(0,str(ROOT/'backend'))
        import cbor2
        from app.communication.esp32.protocol import HEADER, MAGIC, VERSION, cobs_encode, crc32c
        for vector in vectors:
            if 'base' in vector:
                base=next(v for v in vectors if v['name']==vector['base'])
                vector.update({k:base[k] for k in ('message_type','sequence','timestamp_ns')})
                vector['payload']={**base['payload'],**vector.get('overrides',{})}
                for key in vector.get('remove',[]):vector['payload'].pop(key,None)
            if 'header_timestamp_ns' in vector:vector['timestamp_ns']=vector['header_timestamp_ns']
            raw=bytes.fromhex(vector['raw_cbor_hex']) if 'raw_cbor_hex' in vector else cbor2.dumps(vector['payload'],canonical=True)
            body=HEADER.pack(MAGIC,vector.get('frame_version',VERSION),vector['message_type'],len(raw),vector['sequence'],vector['timestamp_ns'])+raw
            checksum=crc32c(body)
            frame=b'\0'+cobs_encode(body+struct.pack('!I',checksum ^ int(vector.get('corrupt_crc',False))))+b'\0'
            if vector.get('truncate_frame'):frame=frame[:-1]
            vector['cbor_hex']=raw.hex().upper()
            vector['frame_hex']=frame.hex().upper()
            vector['crc32c']=f'{checksum:08X}'
        (ROOT/f'{source_name}.json').write_text(json.dumps(vectors,indent=2)+'\n')
    (ROOT/f'firmware/esp32/tests/{source_name}.h').write_text(render_header(vectors))
