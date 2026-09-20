import pytest

from app.communication.esp32.usb import Esp32UsbCandidate, Esp32UsbConfig, IdentityGatedESP32UsbTransport


class FakeSerial:
    def __init__(self): self.writes=[]; self.reads=[]; self.closed=False
    def read(self, size): self.reads.append(size); return b""
    def write(self, data): self.writes.append(data); return len(data)
    def close(self): self.closed=True


def test_discovery_does_not_verify_or_open_a_candidate():
    candidate=Esp32UsbCandidate("COM7","Acme","USB serial","abc","1234","5678")
    transport=IdentityGatedESP32UsbTransport(Esp32UsbConfig("COM7",115200), opener=lambda *args,**kwargs: FakeSerial())
    assert transport.identity.state=="UNVERIFIED"
    with pytest.raises(RuntimeError, match="not verified"): transport.open()
    transport.record_verified_identity(candidate,"operator-recorded bench label")
    assert transport.identity.state=="VERIFIED"


def test_open_requires_path_match_and_writes_only_after_explicit_verification():
    serial=FakeSerial(); transport=IdentityGatedESP32UsbTransport(Esp32UsbConfig("COM8",57600), opener=lambda *args,**kwargs: serial)
    with pytest.raises(ValueError): transport.record_verified_identity(Esp32UsbCandidate("COM7",None,None,None,None,None),"evidence")
    transport.record_verified_identity(Esp32UsbCandidate("COM8",None,None,"serial",None,None),"operator evidence")
    assert transport.open() is transport and transport.open() is transport
    assert transport.read(8)==b""; transport.write(b"\x00safe-frame\x00"); transport.close()
    assert serial.reads==[8] and serial.writes==[b"\x00safe-frame\x00"] and serial.closed

def test_verified_gate_is_usable_as_the_single_duplex_serial_endpoint():
    serial=FakeSerial(); transport=IdentityGatedESP32UsbTransport(Esp32UsbConfig("COM9",115200), opener=lambda *args,**kwargs: serial)
    transport.record_verified_identity(Esp32UsbCandidate("COM9",None,None,"board",None,None),"operator evidence")
    transport.open(); transport.write(b"\x00frame\x00"); assert transport.read(1)==b""
