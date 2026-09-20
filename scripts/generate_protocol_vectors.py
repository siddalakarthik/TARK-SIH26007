"""Generate the C host-test header from Protocol V1's canonical JSON vectors."""
from __future__ import annotations
import json
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
    return "\n".join(lines)+"\n"
if __name__=="__main__":
    vectors=json.loads((ROOT/"protocol_vectors.json").read_text())
    (ROOT/"firmware/esp32/tests/protocol_vectors.h").write_text(render_header(vectors))
