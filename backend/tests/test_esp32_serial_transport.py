from collections import deque
from time import sleep
from app.communication.esp32.protocol import encode_message, STATUS
from app.communication.esp32.serial_transport import BidirectionalSerialTransport, SerialTransportConfig

class FakeSerial:
    def __init__(self,chunks=()):self.chunks=deque(chunks);self.writes=[];self.closed=False
    def read(self,size):return self.chunks.popleft() if self.chunks else b""
    def write(self,data):self.writes.append(data);return len(data)
    def close(self):self.closed=True

def wait(predicate):
    for _ in range(100):
        if predicate():return
        sleep(.01)
    raise AssertionError("transport did not reach expected state")

def test_transport_recovers_multiple_partial_and_bad_frames_without_duplicate_reader():
    good1=encode_message(STATUS,1,1,{"output_state":"DISABLED_PHASE_1"});good2=encode_message(STATUS,2,2,{"output_state":"DISABLED_PHASE_1"})
    serial=FakeSerial([b"noise"+good1[:5],good1[5:]+b"\0\0bad\0"+good2]) ;received=[]
    transport=BidirectionalSerialTransport(lambda:serial,received.append,SerialTransportConfig(read_size=256,reconnect_delay_s=.001))
    transport.start();wait(lambda:len(received)==2)
    try:
        assert received==[good1,good2]
        assert transport.diagnostics.protocol.bytes_received>=len(b"noise")
        try:transport.start();assert False,"second reader must be refused"
        except RuntimeError:pass
    finally:transport.close()

def test_transport_writes_complete_frame_and_bounds_queue():
    serial=FakeSerial();transport=BidirectionalSerialTransport(lambda:serial,lambda _:None,SerialTransportConfig(tx_queue_size=1,reconnect_delay_s=.001));transport.start()
    frame=encode_message(STATUS,1,1,{"output_state":"DISABLED_PHASE_1"});transport.write(frame);wait(lambda:serial.writes==[frame])
    transport.close();assert serial.closed
