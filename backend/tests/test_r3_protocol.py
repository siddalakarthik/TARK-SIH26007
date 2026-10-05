import json
import os
from pathlib import Path
import shutil
import subprocess
import pytest
from app.communication.esp32.protocol import *

ROOT=Path(__file__).parents[2]
VECTORS=json.loads((ROOT/'r3_protocol_vectors.json').read_text())

class Wire:
    def __init__(self): self.frames=[]
    def write(self,frame): self.frames.append(frame)

def observation_client():
    wire=Wire(); c=ESP32Client(wire,nonce_factory=lambda:'2'*32)
    c.open_observation_session('x',100)
    assert decode_frame(wire.frames[0])[0]==SESSION_OPEN
    c.receive(encode_message(SESSION_READY,0,100,{'request_id':'2'*32,'configuration_hash':'x',
        'session_id':VECTORS[0]['payload']['session_id'],'source_mode':'REAL'}),101)
    return c,wire

@pytest.mark.parametrize('vector',VECTORS,ids=lambda x:x['name'])
def test_observation_shared_vector_and_no_command_authority(vector):
    expected=bytes.fromhex(vector['frame_hex'])
    assert encode_message(OBSERVATION,vector['sequence'],vector['timestamp_ns'],vector['payload'])==expected
    c,wire=observation_client(); result=c.receive(expected,200)
    assert result.correlation=='OBSERVATION' and not result.accepted and result.output_state=='DISABLED_PHASE_1'
    assert c.pending=={} and c.last_exchange_ns is None and len(wire.frames)==1
    with pytest.raises(ProtocolError,match='OLD_OBSERVATION'): c.receive(expected,201)
    c.reset_session()
    with pytest.raises(ProtocolError): c.receive(expected,202)

@pytest.mark.parametrize('key,value',[('left_count',True),('right_count',2**31),('source_counter',-1),
    ('interval_end_ns',1000001),('lost_edges',-1),('source_mode','REPLAY'),('session_id','old'),('node_id','')])
def test_invalid_observation_payload(key,value):
    p={**VECTORS[0]['payload'],key:value}
    with pytest.raises(ProtocolError): validate_encoder_observation(p,1000000)

def test_observation_crc_failure_and_framing_fragments():
    frame=bytes.fromhex(VECTORS[0]['frame_hex']); accumulator=FrameAccumulator()
    result=[]
    for byte in frame: result.extend(accumulator.decode(bytes([byte])))
    assert len(result)==1 and result[0][0]==OBSERVATION
    raw=cobs_decode(frame[1:-1]); damaged=b'\0'+cobs_encode(raw[:-1]+bytes([raw[-1]^1]))+b'\0'
    with pytest.raises(ProtocolError,match='CRC32C'): decode_frame(damaged)

def test_shared_c_header_matches_inventory():
    import importlib.util
    spec=importlib.util.spec_from_file_location('vectors',ROOT/'scripts/generate_protocol_vectors.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert module.render_header(VECTORS)==(ROOT/'firmware/esp32/tests/r3_protocol_vectors.h').read_text()

def test_r3_firmware_encoder_interoperability(tmp_path):
    compiler=shutil.which('gcc') or 'C:/msys64/ucrt64/bin/gcc.exe'
    binary=tmp_path/('r3_observation_host.exe' if os.name=='nt' else 'r3_observation_host')
    sources=['tests/r3_observation_host.c','main/protocol/response.c','main/protocol/tark_protocol.c','main/protocol/command_payload.c']
    env={**os.environ,'PATH':str(Path(compiler).parent)+os.pathsep+os.environ.get('PATH','')}
    result=subprocess.run([compiler,'-std=c11','-Wall','-Wextra','-Werror',*[str(ROOT/'firmware/esp32'/s) for s in sources],'-lm','-o',str(binary)],capture_output=True,text=True,timeout=30,env=env)
    assert result.returncode==0,result.stderr
    # OS execution denial must surface as a failure, never a passing skip.
    result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=10,env=env)
    assert result.returncode==0,result.stdout+result.stderr
    frames=[bytes.fromhex(line[6:]) for line in result.stdout.splitlines() if line.startswith('FRAME ')]
    assert len(frames)==len(VECTORS)
    for frame,vector in zip(frames,VECTORS):
        c,_=observation_client(); assert c.receive(frame,200).payload==vector['payload']
