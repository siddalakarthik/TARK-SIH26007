import pytest
from app.communication.esp32.protocol import *
from app.domain.models import BoundedCommand, SafetyState, ReasonCode
SID='111111111111111111111111111111110000000000000001'

def command(seq=1,valid=1_500_000_000):
    return BoundedCommand(sequence=seq,timestamp_ns=1_000_000_000,valid_until_ns=valid,state=SafetyState.UNKNOWN,permitted_speed_mps=0,left_command=0,right_command=0,heartbeat=seq,reason_code=ReasonCode.UNKNOWN_STALE,configuration_hash='x')

def test_round_trip_crc32c_cobs():
    message,value=decode_frame(encode_command(command(),SID));assert message==COMMAND and value['payload']['sequence']==1

def test_corruption_is_rejected():
    frame=bytearray(encode_command(command(),SID));frame[4]^=1
    with pytest.raises(ProtocolError):decode_frame(bytes(frame))

def test_expired_and_old_commands_rejected():
    c=ESP32Client(ESP32ProtocolSimulator('x'))
    assert not c.submit(command(valid=999),1_000_000_000).accepted
    assert c.submit(command(2),1_000_000_000).accepted
    assert not c.submit(command(2),1_000_000_000).accepted

def test_simulated_endpoint_acknowledges_but_never_claims_output():
    endpoint=ESP32ProtocolSimulator('x');client=ESP32Client(endpoint)
    assert client.submit(command(),1_000_000_000).accepted
    feedback=client.receive(endpoint.last_response,1_000_000_001)
    assert feedback.accepted and feedback.output_state==OUTPUT_STATE
    assert feedback.payload['source_mode']=='SIMULATION' and feedback.payload['applied_left']==feedback.payload['applied_right']==0

def test_simulated_endpoint_rejects_bad_configuration_and_replay():
    endpoint=ESP32ProtocolSimulator('x');client=ESP32Client(endpoint)
    assert client.submit(command(),1_000_000_000).accepted
    assert client.receive(endpoint.last_response,1_000_000_001).accepted
    endpoint.write(encode_command(command(),client.session_id))
    assert decode_frame(endpoint.last_response)[1]['payload']['reason']=='DUPLICATE_SEQUENCE'
    with pytest.raises(ProtocolError):client.receive(endpoint.last_response,1_000_000_002)
    bad=command(2);bad.configuration_hash='wrong'
    endpoint.write(encode_command(bad,client.session_id))
    assert decode_frame(endpoint.last_response)[1]['payload']['reason']=='CONFIGURATION_MISMATCH'

def test_command_range_and_uint32_sequence_are_rejected_before_transport():
    client=ESP32Client();bad=command();bad.left_command=1.1
    assert client.submit(bad,1_000_000_000).reason=='COMMAND_OUT_OF_RANGE'
    assert client.submit(command(seq=0x1_0000_0000),1_000_000_000).reason=='COMMAND_SEQUENCE_OUT_OF_RANGE'

def test_pi_rx_recovers_after_corrupt_frame_and_correlates_only_exact_sequence():
    endpoint=ESP32ProtocolSimulator('x');client=ESP32Client(endpoint)
    assert client.submit(command(1),1_000_000_000).accepted and client.submit(command(2),1_000_000_000).accepted
    good=endpoint.last_response;bad=bytearray(good);bad[-2]^=1
    stream=FrameAccumulator();assert len(stream.decode(bytes(bad)+good))==1 and stream.counters.crc_failures==1
    feedback=client.receive(good,1_000_000_001)
    assert feedback.sequence==2 and feedback.correlation=='MATCHED' and 1 in client.pending
    status=encode_message(STATUS,99,1,{'output_state':OUTPUT_STATE,'reason':'NONE','source_mode':'SIMULATION','session_id':client.session_id,'configuration_hash':'x'})
    with pytest.raises(ProtocolError):client.receive(status,1_000_000_002)
