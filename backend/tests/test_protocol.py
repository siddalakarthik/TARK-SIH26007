import pytest
from app.communication.esp32.protocol import decode_frame, encode_command, encode_message, ESP32Client, ESP32ProtocolSimulator, FrameAccumulator, NACK, STATUS
from app.domain.models import BoundedCommand, SafetyState, ReasonCode
def command(seq=1,valid=2_000_000_000): return BoundedCommand(sequence=seq,timestamp_ns=1_000_000_000,valid_until_ns=valid,state=SafetyState.UNKNOWN,permitted_speed_mps=0,left_command=0,right_command=0,heartbeat=seq,reason_code=ReasonCode.UNKNOWN_STALE,configuration_hash="x")
def test_round_trip_crc32c_cobs():
    msg,payload=decode_frame(encode_command(command())); assert msg==1 and payload["payload"]["sequence"]==1
def test_corruption_is_rejected():
    frame=bytearray(encode_command(command())); frame[4]^=1
    with pytest.raises(ValueError): decode_frame(bytes(frame))
def test_expired_and_old_commands_rejected():
    c=ESP32Client(); assert not c.submit(command(valid=999),1000).accepted
    assert c.submit(command(2),1000).accepted and not c.submit(command(2),1000).accepted
def test_simulated_endpoint_acknowledges_but_never_claims_output():
    endpoint=ESP32ProtocolSimulator("x"); client=ESP32Client(endpoint)
    assert client.submit(command(),1_000_000_000).accepted
    feedback=client.receive(endpoint.last_response)
    assert feedback.accepted and feedback.output_state=="DISABLED_PHASE_1"
    assert feedback.payload["applied_left"]==0.0 and feedback.payload["applied_right"]==0.0
def test_simulated_endpoint_rejects_bad_configuration_and_replay():
    endpoint=ESP32ProtocolSimulator("reviewed"); client=ESP32Client(endpoint)
    assert client.submit(command(),1_000_000_000).accepted
    feedback=client.receive(endpoint.last_response)
    assert not feedback.accepted and feedback.message_type==NACK and feedback.reason=="CONFIGURATION_MISMATCH"
    accepted=command(seq=2); accepted.configuration_hash="reviewed"
    assert client.submit(accepted,1_000_000_000).accepted; assert client.receive(endpoint.last_response).accepted
    # Direct replay injection red-teams the endpoint independently of the Pi-side sequence guard.
    endpoint.write(encode_command(accepted)); assert endpoint.last_response is not None
    assert client.receive(endpoint.last_response).reason=="DUPLICATE_SEQUENCE"
def test_command_range_and_uint32_sequence_are_rejected_before_transport():
    client=ESP32Client(); bad=command(); bad.left_command=1.1
    assert client.submit(bad,1_000_000_000).reason=="COMMAND_OUT_OF_RANGE"
    too_large=command(seq=0x1_0000_0000)
    assert client.submit(too_large,1_000_000_000).reason=="COMMAND_SEQUENCE_OUT_OF_RANGE"
def test_pi_rx_recovers_after_corrupt_frame_and_correlates_only_exact_sequence():
    endpoint=ESP32ProtocolSimulator("x"); client=ESP32Client(endpoint)
    first=command(seq=1); second=command(seq=2)
    assert client.submit(first,1_000_000_000).accepted and client.submit(second,1_000_000_000).accepted
    good=endpoint.last_response; assert good is not None
    bad=bytearray(good); bad[-2]^=1
    stream=FrameAccumulator(); received=stream.decode(bytes(bad)+good)
    assert len(received)==1 and stream.counters.crc_failures==1
    response=client.receive(good)
    assert response.sequence==2 and response.correlation=="MATCHED" and 1 in client.pending
    status=encode_message(STATUS,99,1,{"output_state":"DISABLED_PHASE_1","reason":"NONE"})
    assert client.receive(status).correlation=="UNKNOWN_OR_LATE"
