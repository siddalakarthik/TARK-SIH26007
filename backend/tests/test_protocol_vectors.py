import json
import importlib.util
from pathlib import Path
import cbor2
from app.communication.esp32.protocol import cobs_decode, crc32c, decode_frame, encode_message

ROOT=Path(__file__).parents[2]
VECTORS=json.loads((ROOT/"protocol_vectors.json").read_text())

def test_canonical_vectors_are_independent_expected_values():
    for vector in VECTORS:
        frame=bytes.fromhex(vector["frame_hex"]); payload=cbor2.dumps(vector["payload"],canonical=True)
        assert payload.hex().upper()==vector["cbor_hex"]
        raw=cobs_decode(frame[1:-1])
        assert crc32c(raw[:-4])==int(vector["crc32c"],16)
        assert encode_message(vector["message_type"],vector["sequence"],vector["timestamp_ns"],vector["payload"])==frame
        message,envelope=decode_frame(frame)
        assert message==vector["message_type"] and envelope["sequence"]==vector["sequence"] and envelope["timestamp_ns"]==vector["timestamp_ns"] and envelope["payload"]==vector["payload"]

def test_generated_c_header_is_current():
    spec=importlib.util.spec_from_file_location("vectors",ROOT/"scripts/generate_protocol_vectors.py")
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    header=(ROOT/"firmware/esp32/tests/protocol_vectors.h").read_text()
    assert header==module.render_header(VECTORS)
