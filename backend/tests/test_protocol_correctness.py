from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess
import pytest
from app.communication.esp32.protocol import *
from app.communication.esp32.serial_transport import BidirectionalSerialTransport
from test_protocol import command, SID

ROOT=Path(__file__).parents[2]
VECTORS=json.loads((ROOT/'protocol_vectors.json').read_text())

@pytest.fixture(scope='module')
def host(tmp_path_factory):
    compiler=shutil.which('gcc')
    if compiler is None and Path('C:/msys64/ucrt64/bin/gcc.exe').is_file():compiler='C:/msys64/ucrt64/bin/gcc.exe'
    assert compiler,'Strict firmware host compilation requires GCC; do not skip this gate'
    directory=tmp_path_factory.mktemp('protocol-host')
    common=['protocol/tark_protocol.c','protocol/command_payload.c','protocol/response.c','protocol/service.c',
            'command/command_supervisor.c','hardware/motor_driver.c','hardware/encoder.c','safety/watchdog.c']
    env=os.environ.copy();env['PATH']=str(Path(compiler).parent)+os.pathsep+env.get('PATH','')
    for name in ['host_test','task7b_host_test','interop_host']:
        executable=directory/(name+('.exe' if os.name=='nt' else ''))
        result=subprocess.run([compiler,'-std=c11','-Wall','-Wextra','-Werror',str(ROOT/f'firmware/esp32/tests/{name}.c'),
                               *[str(ROOT/'firmware/esp32/main'/p) for p in common],'-lm','-o',str(executable)],capture_output=True,text=True,timeout=30,env=env)
        assert result.returncode==0,result.stdout+result.stderr
        if name!='interop_host':
            result=subprocess.run([str(executable)],capture_output=True,text=True,timeout=10,env=env)
            assert result.returncode==0,result.stdout+result.stderr
    def run(lines):
        result=subprocess.run([str(executable)],input='\n'.join(lines)+'\n',capture_output=True,text=True,timeout=15,env=env)
        assert result.returncode==0,result.stdout+result.stderr
        return result.stdout.splitlines()
    return run

def frames(lines):return [bytes.fromhex(line.split()[1]) for line in lines if line.startswith('FRAME ')]

def test_every_shared_vector_through_real_c_decoder(host):
    lines=host([f'CHECK 12000000000 {v["frame_hex"]}' for v in VECTORS])
    assert len(lines)==len(VECTORS)
    for v,line in zip(VECTORS,lines):
        valid=v.get('expect_frame_valid',True) and v.get('expect_canonical',True) and v.get('expect_command_valid',True)
        assert line.startswith('CHECK OK' if valid else 'CHECK REJECT'),(v['name'],line)
        if valid and v['message_type']==COMMAND:
            _,_,expiry,speed,left,right=line.split()
            p=v['payload'];assert int(expiry)==12_000_000_000+p['valid_until_ns']-p['timestamp_ns']
            assert (float(speed),float(left),float(right))==tuple(p[k] for k in ('permitted_speed_mps','left_command','right_command'))

@pytest.mark.parametrize('sender,receiver',[(28_800_000_000_000,12_000_000_000),(12_000_000_000,28_800_000_000_000)])
@pytest.mark.parametrize('ttl',[0,1,250_000_000,500_000_000,500_000_001,99_000_000_000_000])
def test_independent_clock_and_ttl_boundaries_in_python_and_c(host,sender,receiver,ttl):
    c=command().model_copy(update={'timestamp_ns':sender,'valid_until_ns':sender+ttl})
    frame=encode_command(c,SID);payload=decode_frame(frame)[1]['payload']
    reason=validate_command_payload(payload,1,sender,receiver,'x',SID)
    line=host([f'CHECK {receiver} {frame.hex()}'])[0]
    assert (reason is None)==(0<ttl<=MAX_COMMAND_LIFETIME_NS)
    assert line.startswith('CHECK OK' if reason is None else 'CHECK REJECT')
    if reason is None:assert int(line.split()[2])==receiver+ttl

def test_receiver_expiry_overflow_rejected_by_both(host):
    c=command();p=decode_frame(encode_command(c,SID))[1]['payload']
    assert validate_command_payload(p,1,c.timestamp_ns,MAX_UINT64,'x',SID)=='INVALID_LIFETIME'
    assert host([f'CHECK {MAX_UINT64} {encode_command(c,SID).hex()}'])[0]=='CHECK REJECT INVALID_LIFETIME'

class Wire:
    def __init__(self):self.frames=[]
    def write(self,frame):self.frames.append(frame)

def test_python_command_c_supervisor_responses_python_decode_and_no_frame_expiry(host):
    transport=Wire();client=ESP32Client(transport,nonce_factory=lambda:'2'*32)
    c=command();assert client.submit(c,c.timestamp_ns).reason=='SESSION_PENDING'
    session_response=frames(host([f'RX 12000000000 {transport.frames[0].hex()}']))[0]
    assert client.receive(session_response,c.timestamp_ns) is None
    assert client.submit(c,c.timestamp_ns).accepted
    result=host([f'RX 12000000000 {transport.frames[0].hex()}',f'RX 12000000000 {transport.frames[1].hex()}',
                 'TICK 12499999999','TICK 12500000000','TICK 12750000000'])
    responses=frames(result)
    ack=client.receive(responses[1],c.timestamp_ns+1)
    assert ack.accepted and ack.payload['source_mode']=='REAL' and ack.payload['applied_left']==ack.payload['applied_right']==0
    status=client.receive(responses[-1],c.timestamp_ns+2)
    assert status.message_type==STATUS and status.reason=='COMMAND_EXPIRED'
    assert any(line.startswith('STATE 0 12500000000 1 1 COMMAND_EXPIRED') for line in result)
    assert client.health(c.timestamp_ns+MAX_COMMAND_LIFETIME_NS+1)['state']=='STALE'

def test_c_reboot_old_session_rejected_new_session_accepts(host):
    old=encode_command(command(),SID)
    new_sid='3'*32+'0000000000000001'
    new=encode_command(command(),new_sid)
    opened=next(v['frame_hex'] for v in VECTORS if v['name']=='session_open')
    result=frames(host([f'RX 12000000000 {opened}',f'RX 12000000000 {old.hex()}',
                       'BOOT 0 '+('3'*32),f'RX 12000000000 {opened}',f'RX 12000000000 {old.hex()}',f'RX 12000000000 {new.hex()}']))
    decoded=[decode_frame(frame) for frame in result]
    assert decoded[-2][0]==NACK and decoded[-2][1]['payload']['reason']=='SESSION_MISMATCH'
    assert decoded[-1][0]==ACK and decoded[-1][1]['payload']['session_id']==new_sid

@pytest.mark.parametrize('mutation',['empty','missing','accepted_type','wrong_kind','output','nonzero','wrong_sequence','wrong_timestamp','wrong_config','wrong_session','wrong_source','extra','bad_reason','heartbeat_reason','bad_crc','late'])
def test_invalid_responses_never_become_health_evidence(mutation):
    endpoint=ESP32ProtocolSimulator('x');client=ESP32Client(endpoint)
    assert client.submit(command(),1_000_000_000).accepted
    message,e=decode_frame(endpoint.last_response);p=e['payload'];q=e['sequence'];stamp=e['timestamp_ns'];now=1_000_000_001
    if mutation=='empty':p={}
    elif mutation=='missing':p.pop('applied_left')
    elif mutation=='accepted_type':p['accepted']=1
    elif mutation=='wrong_kind':message=NACK
    elif mutation=='output':p['output_state']='ENABLED'
    elif mutation=='nonzero':p['applied_left']=.1
    elif mutation=='wrong_sequence':q=2
    elif mutation=='wrong_timestamp':stamp+=1
    elif mutation=='wrong_config':p['configuration_hash']='other'
    elif mutation=='wrong_session':p['session_id']='3'*48
    elif mutation=='wrong_source':p['source_mode']='REAL'
    elif mutation=='extra':p['unknown']=1
    elif mutation=='bad_reason':p['reason']='FINE'
    elif mutation=='heartbeat_reason':p['reason']='HEARTBEAT_ACCEPTED'
    elif mutation=='late':now=1_500_000_000
    frame=encode_message(message,q,stamp,p)
    if mutation=='bad_crc':frame=frame[:-2]+bytes([frame[-2]^1])+frame[-1:]
    with pytest.raises(ProtocolError):client.receive(frame,now)
    assert client.last_exchange_ns is None and client.health(now)['state']=='NOT_CONNECTED'

def test_old_ack_after_new_session_and_duplicate_feedback_rejected():
    endpoint=ESP32ProtocolSimulator('x',boot_id='1'*32);client=ESP32Client(endpoint)
    client.submit(command(),1_000_000_000);old=endpoint.last_response
    client.reset_session();client.transport=ESP32ProtocolSimulator('x',boot_id='3'*32)
    client.submit(command(),1_000_000_000);current=client.transport.last_response
    with pytest.raises(ProtocolError):client.receive(old,1_000_000_001)
    assert client.receive(current,1_000_000_001).accepted
    with pytest.raises(ProtocolError):client.receive(current,1_000_000_002)

def test_pending_stress_and_concurrent_submission_are_bounded():
    endpoint=ESP32ProtocolSimulator('x');client=ESP32Client(endpoint)
    for seq in range(1,5001):client.submit(command(seq),1_000_000_000)
    assert len(client.pending)==MAX_PENDING and len(client.terminal)<=256
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda q:client.submit(command(q),1_000_000_000),range(5001,5101)))
    assert len(client.pending)<=MAX_PENDING
    assert client.expire_pending(1_500_000_000) and not client.pending
    assert all(state in {'SUPERSEDED','EXPIRED'} for _,state in client.terminal)

def test_nack_is_correlated_rejection_not_online():
    endpoint=ESP32ProtocolSimulator('x');client=ESP32Client(endpoint);client.submit(command(),1_000_000_000)
    _,e=decode_frame(endpoint.last_response);p={**e['payload'],'accepted':False,'reason':'CONFIGURATION_MISMATCH'}
    response=client.receive(encode_message(NACK,1,1_000_000_000,p),1_000_000_001)
    assert not response.accepted and client.health(1_000_000_002)['state']=='DEGRADED'
    assert client.terminal[-1]==(1,'REJECTED')

class PartialPort:
    def __init__(self,counts):self.counts=list(counts);self.output=bytearray();self.closed=False
    def write(self,data):
        n=self.counts.pop(0) if self.counts else len(data)
        if n=='error':raise OSError('fixture unplug')
        if n is not None and n>0:self.output.extend(data[:n])
        return n
    def close(self):self.closed=True

def test_partial_writes_complete_only_within_one_connection():
    port=PartialPort([1,2,3]);transport=BidirectionalSerialTransport(lambda:port,lambda _:None,clock=lambda:1_000_000_000)
    assert transport._connect();frame=encode_command(command(),SID);transport.write(frame)
    assert transport._write_one(port) and bytes(port.output)==frame and transport.diagnostics.tx_written==1
    transport.close()

@pytest.mark.parametrize('failure',[0,None,'error'])
def test_failed_partial_write_reconnect_flushes_tail_queue_and_rx(failure):
    first=PartialPort([3,failure]);second=PartialPort([]);ports=iter([first,second]);resets=[]
    transport=BidirectionalSerialTransport(lambda:next(ports),lambda _:None,on_reset=lambda:resets.append(1),clock=lambda:1_000_000_000)
    transport._connect();frame=encode_command(command(),SID);transport.write(frame);transport.write(frame);transport._frames.feed(frame[:10])
    with pytest.raises((RuntimeError,OSError)):transport._write_one(first)
    transport._close_serial();transport._connect()
    assert not transport._write_one(second) and not second.output and not transport._frames._buffer
    assert len(resets)==3 and transport.diagnostics.tx_written==0
    transport.close()

def test_queue_deadline_expires_without_writing():
    now=[1_000_000_000];port=PartialPort([])
    transport=BidirectionalSerialTransport(lambda:port,lambda _:None,clock=lambda:now[0]);transport._connect()
    transport.write(encode_command(command(),SID));now[0]=1_500_000_000
    transport._write_one(port);assert not port.output and transport.diagnostics.tx_dropped==1
    transport.close()

def test_heartbeat_does_not_extend_command_expiry_in_python_or_c(host):
    now=[12_000_000_000];endpoint=ESP32ProtocolSimulator('x',clock=lambda:now[0],boot_id='1'*32)
    client=ESP32Client(endpoint);client.submit(command(),1_000_000_000);client.receive(endpoint.last_response,1_000_000_001)
    now[0]+=400_000_000;client.submit_heartbeat(2,1_400_000_000)
    assert client.receive(endpoint.last_response,1_400_000_001).reason=='HEARTBEAT_ACCEPTED'
    assert endpoint.local_expiry_ns==12_500_000_000
    endpoint.tick(12_500_000_000);assert endpoint.last_reason=='COMMAND_EXPIRED'
    opened=next(v['frame_hex'] for v in VECTORS if v['name']=='session_open')
    heartbeat=encode_heartbeat(2,1_400_000_000,'x',SID)
    lines=host([f'RX 12000000000 {opened}',f'RX 12000000000 {encode_command(command(),SID).hex()}',
                f'RX 12400000000 {heartbeat.hex()}','TICK 12500000000'])
    assert decode_frame(frames(lines)[-2])[1]['payload']['reason']=='HEARTBEAT_ACCEPTED'
    assert lines[-1].startswith('STATE 0 12500000000 2 1 COMMAND_EXPIRED')

def test_unknown_status_and_legacy_frame_never_create_authority(host):
    endpoint=ESP32ProtocolSimulator('x');client=ESP32Client(endpoint);client.submit(command(),1_000_000_000)
    client.receive(endpoint.last_response,1_000_000_001)
    p={'reason':'SAFE','output_state':OUTPUT_STATE,'configuration_hash':'x','session_id':client.session_id,'source_mode':'SIMULATION'}
    with pytest.raises(ProtocolError,match='INVALID_STATUS_REASON'):client.receive(encode_message(STATUS,1,12,p),1_000_000_002)
    valid=encode_command(command(),SID);raw=bytearray(cobs_decode(valid[1:-1]));raw[2]=1
    raw[-4:]=struct.pack('!I',crc32c(raw[:-4]));legacy=b'\0'+cobs_encode(raw)+b'\0'
    with pytest.raises(ProtocolError,match='unsupported protocol version'):decode_frame(legacy)
    assert host([f'CHECK 12000000000 {legacy.hex()}'])[0]=='CHECK REJECT FRAME'
    with pytest.raises(ProtocolError):cobs_decode(bytes([2,0]))

def test_failed_handshake_is_not_online_and_stale_feedback_is_cleared():
    wire=Wire();client=ESP32Client(wire,nonce_factory=lambda:'2'*32)
    assert client.submit(command(),1_000_000_000).reason=='SESSION_PENDING'
    ready=next(bytes.fromhex(v['frame_hex']) for v in VECTORS if v['name']=='session_ready')
    with pytest.raises(ProtocolError):client.receive(ready,1_500_000_000)
    assert client.health(1_500_000_000)['state']=='NOT_CONNECTED'
    endpoint=ESP32ProtocolSimulator('x');client=ESP32Client(endpoint);client.submit(command(),1_000_000_000)
    client.receive(endpoint.last_response,1_000_000_001)
    assert client.feedback_snapshot(1_000_000_002)['accepted']
    assert client.feedback_snapshot(1_500_000_001) is None

def test_reconnect_thread_alone_is_not_online(monkeypatch):
    from app.services.system import TarkSystem
    from app.config import Settings
    monkeypatch.setenv('TARK_DATABASE_PATH',':memory:')
    system=TarkSystem(Settings.from_file(ROOT/'config/phase1.json'))
    class Worker:
        running=True
        def close(self):pass
    system.esp32_transport=Worker()
    try:
        state=next(s for s in system.sensor_snapshot(1_000_000_000) if s['device_id']=='esp32')
        assert state['state']=='NOT_CONNECTED' and state['source_mode']=='NOT_CONNECTED' and state['worker_running']
    finally:system.close()

def test_receiver_reboot_without_port_disconnect_forces_new_session():
    endpoint=ESP32ProtocolSimulator('x',boot_id='1'*32);client=ESP32Client(endpoint)
    assert client.submit(command(),1_000_000_000).accepted
    client.receive(endpoint.last_response,1_000_000_001);old_session=client.session_id
    # Same transport slot, a fresh receiver process with no negotiated session.
    client.transport=ESP32ProtocolSimulator('x',boot_id='3'*32)
    second=command(2).model_copy(update={'timestamp_ns':1_250_000_000,'valid_until_ns':1_750_000_000})
    assert client.submit(second,1_250_000_000).accepted and client.transport.last_response is None
    client.expire_pending(1_750_000_000);assert client.session_id is None
    third=command(3).model_copy(update={'timestamp_ns':1_750_000_000,'valid_until_ns':2_250_000_000})
    assert client.submit(third,1_750_000_000).accepted and client.session_id!=old_session
    assert client.receive(client.transport.last_response,1_750_000_001).accepted

@pytest.mark.parametrize('field',sorted(COMMAND_FIELDS))
def test_missing_required_fields_have_same_python_c_rejection(host,field):
    payload=decode_frame(encode_command(command(),SID))[1]['payload']
    payload.pop(field)
    assert validate_command_payload(payload,1,1_000_000_000,12_000_000_000,'x',SID)=='INVALID_PAYLOAD'
    frame=encode_message(COMMAND,1,1_000_000_000,payload)
    assert host([f'CHECK 12000000000 {frame.hex()}'])[0]=='CHECK REJECT INVALID_PAYLOAD'

def test_receiver_clock_rollback_and_bad_handshake_fail_closed(host):
    now=[12_000_000_000];endpoint=ESP32ProtocolSimulator('x',clock=lambda:now[0],boot_id='1'*32)
    client=ESP32Client(endpoint);client.submit(command(),1_000_000_000)
    assert endpoint.local_expiry_ns is not None
    now[0]-=1;endpoint.write(encode_command(command(2),SID))
    assert endpoint.local_expiry_ns is None and endpoint.last_reason=='INTERNAL_FAULT' and endpoint.last_response is None
    opened=next(v['frame_hex'] for v in VECTORS if v['name']=='session_open')
    lines=host([f'RX 12000000000 {opened}',f'RX 12000000000 {encode_command(command(),SID).hex()}',
                f'RX 11999999999 {encode_command(command(2),SID).hex()}'])
    assert lines[-1].startswith('STATE 0 12500000000 1 1 INTERNAL_FAULT')
    now[0]=12_100_000_000;endpoint.write(encode_command(command(2),SID))
    bad=encode_message(SESSION_OPEN,0,1_100_000_000,{'request_id':'2'*32,'configuration_hash':'wrong'})
    endpoint.write(bad)
    assert endpoint.local_expiry_ns is None and endpoint.last_reason=='INVALID_PAYLOAD'

def test_transport_reset_callback_failure_does_not_leak_serial():
    port=PartialPort([])
    def broken():raise RuntimeError('fixture reset failed')
    transport=BidirectionalSerialTransport(lambda:port,lambda _:None,on_reset=broken)
    assert not transport._connect() and port.closed and not transport.connected
    transport.close()
