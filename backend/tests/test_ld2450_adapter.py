from app.sensors.ld2450.adapter import LD2450Adapter


class FakeSerial:
    def read_until(self, _marker, _limit): return b"unknown-vendor-frame"
    def close(self): pass


def test_raw_capture_sink_retains_undecoded_bytes_without_claiming_a_decoder():
    captured=[]
    adapter=LD2450Adapter("UNUSED", raw_sink=lambda timestamp, raw: captured.append((timestamp,raw)))
    adapter._serial=FakeSerial()
    timestamp, raw=adapter.read()
    assert captured==[(timestamp,raw)]
    assert adapter.diagnostics()["protocol"]=="VENDOR_FRAME_SPEC_REQUIRED"
