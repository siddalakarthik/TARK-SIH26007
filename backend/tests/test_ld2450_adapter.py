import time

from app.sensors.ld2450.adapter import LD2450Adapter, LD2450RawCaptureWorker


def target_report() -> bytes:
    # One documented sign/magnitude target: -0.100 m, +0.200 m, -0.10 m/s.
    slot = b"\x64\x00\xC8\x80\x0A\x00\x0A\x00"
    return b"\xAA\xFF\x03\x00" + slot + b"\0" * 16 + b"\x55\xCC"


class FakeSerial:
    def read(self, _limit): return b"unknown-vendor-frame"
    def close(self): pass


def test_raw_capture_sink_retains_bytes_with_documented_decoder_available():
    captured=[]
    adapter=LD2450Adapter("UNUSED", raw_sink=lambda timestamp, raw: captured.append((timestamp,raw)))
    adapter._serial=FakeSerial()
    timestamp, raw=adapter.read()
    assert captured==[(timestamp,raw)]
    assert adapter.diagnostics()["protocol"]=="HLK_LD2450_TARGET_REPORT_V1_03"


def test_worker_reconnects_and_emits_only_decoded_documented_reports():
    class FakeAdapter:
        def __init__(self): self.opens=0; self.closed=False; self.sent=False
        def open(self):
            self.opens += 1
            if self.opens == 1: raise RuntimeError("temporary fixture disconnect")
        def read(self):
            time.sleep(.002)
            if not self.sent:
                self.sent=True
                return 99, target_report()
            return 100, b"noise"
        def close(self): self.closed=True
        def diagnostics(self): return {"last_timestamp_ns":99,"last_byte_count":30,"last_error":None}

    adapter = FakeAdapter(); received=[]
    worker = LD2450RawCaptureWorker(adapter, reconnect_s=.001, on_report=lambda timestamp, report: received.append((timestamp, report)))
    worker.start()
    for _ in range(100):
        if received: break
        time.sleep(.01)
    worker.close()
    assert adapter.opens >= 2 and adapter.closed
    assert worker.reconnect_count >= 1 and worker.decoded_report_count == 1
    assert received[0][0] == 99 and received[0][1][0].x_m == -0.1
