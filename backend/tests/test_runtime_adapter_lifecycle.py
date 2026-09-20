"""Runtime selection tests use fakes only; they never enumerate or open hardware."""
from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import Mock

from app.camera import CameraConfig, PiUvcCameraAdapter
from app.communication.esp32.usb import Esp32UsbCandidate, IdentityGatedESP32UsbTransport
from app.config import Settings
from app.services.system import TarkSystem


ROOT = Path(__file__).parents[2]


def settings(mode: str = "simulation") -> Settings:
    return Settings.from_file(ROOT / "config" / "phase1.json").model_copy(update={"mode": mode})


def wait_for(predicate, message: str = "worker did not start") -> None:
    for _ in range(100):
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError(message)


def clear_adapter_environment(monkeypatch, tmp_path) -> None:
    for name in (
        "TARK_GNSS_DEVICE_PATH", "TARK_CAMERA_DEVICE_PATH", "TARK_ESP32_DEVICE_PATH",
        "TARK_ESP32_BAUD", "TARK_RADAR_PORT",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "tark.db"))


def nmea(body: str) -> bytes:
    checksum = 0
    for byte in body.encode("ascii"):
        checksum ^= byte
    return f"${body}*{checksum:02X}\r\n".encode("ascii")


def test_simulation_default_creates_no_configured_adapter_workers(monkeypatch, tmp_path):
    clear_adapter_environment(monkeypatch, tmp_path)
    system = TarkSystem(settings())
    try:
        assert system.gnss_reader is None
        assert system.ld2450_capture is None
        assert system.esp32_usb is None
        assert system.camera.health(1).state == "NOT_CONNECTED"
        assert system.tick(1_000_000_000)["vehicle_location"]["location"]["source"] == "SIMULATION"
    finally:
        system.close()


def test_configured_gnss_reader_feeds_existing_callbacks_without_simulation(monkeypatch, tmp_path):
    clear_adapter_environment(monkeypatch, tmp_path)
    monkeypatch.setenv("TARK_GNSS_DEVICE_PATH", "FAKE-GNSS")
    monkeypatch.setenv("TARK_GNSS_RECONNECT_INTERVAL_S", "10")

    class IdlePort:
        closed = False
        def read(self, _size):
            time.sleep(0.005)
            return b""
        def close(self):
            self.closed = True

    port = IdlePort()
    opener_factory = Mock(return_value=lambda: port)
    system = TarkSystem(settings("real_radar"), gnss_opener_factory=opener_factory)
    try:
        assert system.gnss_reader is not None
        wait_for(lambda: system.gnss_reader is not None and system.gnss_reader.diag.transport_connected)
        system.gnss_reader.feed(nmea("GPRMC,123519,A,1723.100,N,07829.202,E,001.0,045.0,230394,,,A"), now_ns=1_000_000_000)
        assert system.vehicle_location(1_000_000_001)["location"]["source"] == "GNSS"
        system.gnss_simulator.fix = Mock(side_effect=AssertionError("simulator must not run"))
        assert system.tick(1_000_000_002)["vehicle_location"]["location"]["source"] == "GNSS"
        system.gnss_simulator.fix.assert_not_called()
    finally:
        system.close()
    assert port.closed


def test_configured_camera_starts_only_in_hardware_capable_mode_and_closes(monkeypatch, tmp_path):
    clear_adapter_environment(monkeypatch, tmp_path)

    class Capture:
        released = False
        def isOpened(self): return False
        def set(self, *_): return True
        def get(self, *_): return 0
        def read(self): return False, None
        def release(self): self.released = True

    class Cv2:
        CAP_PROP_FRAME_WIDTH = 1; CAP_PROP_FRAME_HEIGHT = 2; CAP_PROP_FPS = 3; IMWRITE_JPEG_QUALITY = 4
        def __init__(self): self.capture = Capture()
        def VideoCapture(self, _path): return self.capture

    camera = PiUvcCameraAdapter(CameraConfig(device_path="FAKE-CAMERA", reconnect_s=10), Cv2())
    system = TarkSystem(settings("real_radar"), camera=camera)
    try:
        wait_for(lambda: camera.health(time.monotonic_ns()).state == "ERROR")
        assert camera.health(time.monotonic_ns()).reason.startswith("CAMERA ERROR")
    finally:
        system.close()
    assert camera.read_frame(time.monotonic_ns()).metadata.state == "NOT_CONNECTED"


def test_configured_esp32_stays_identity_gated_until_explicit_mock_verification(monkeypatch, tmp_path):
    clear_adapter_environment(monkeypatch, tmp_path)
    monkeypatch.setenv("TARK_ESP32_DEVICE_PATH", "FAKE-ESP32")
    monkeypatch.setenv("TARK_ESP32_BAUD", "115200")

    class FakeSerial:
        closed = False
        def read(self, _size):
            time.sleep(0.005)
            return b""
        def write(self, _data): return 0
        def close(self): self.closed = True

    serial = FakeSerial()
    def usb_factory(config):
        return IdentityGatedESP32UsbTransport(config, opener=lambda *_args, **_kwargs: serial)

    system = TarkSystem(settings("real_radar"), esp32_usb_factory=usb_factory)
    try:
        assert system.esp32_usb is not None
        assert not system.start_verified_esp32_transport()
        assert system.sensor_snapshot(1)[1]["state"] == "NOT_CONNECTED"
        system.esp32_usb.record_verified_identity(
            Esp32UsbCandidate("FAKE-ESP32", None, None, "test", None, None), "test fixture only"
        )
        assert system.start_verified_esp32_transport()
        wait_for(lambda: system.esp32_transport is not None and system.esp32_transport.running)
        snapshot = system.tick(1_000_000_000)
        assert snapshot["traction"] == "DISABLED_PHASE_1"
        assert snapshot["command"]["left_command"] == snapshot["command"]["right_command"] == 0
    finally:
        system.close()
    assert serial.closed


def test_configured_ld2450_retains_raw_bytes_without_false_simulation(monkeypatch, tmp_path):
    clear_adapter_environment(monkeypatch, tmp_path)
    monkeypatch.setenv("TARK_RADAR_PORT", "FAKE-LD2450")
    monkeypatch.setenv("TARK_RADAR_RECONNECT_INTERVAL_S", "10")

    class FakeRawAdapter:
        def __init__(self, _port, _baud, raw_sink):
            self.raw_sink = raw_sink; self.closed = False; self.reads = 0
        def open(self): pass
        def read(self):
            time.sleep(0.005)
            self.reads += 1
            self.raw_sink(1_000_000_000 + self.reads, b"unverified-vendor-frame")
            return 1_000_000_000 + self.reads, b"unverified-vendor-frame"
        def close(self): self.closed = True
        def diagnostics(self):
            return {"state": "NOT_CONNECTED", "protocol": "HLK_LD2450_TARGET_REPORT_V1_03", "last_timestamp_ns": None, "last_byte_count": 23, "last_error": None}

    captured = []
    def factory(*args):
        adapter = FakeRawAdapter(*args)
        captured.append(adapter)
        return adapter

    system = TarkSystem(settings("real_radar"), ld2450_factory=factory)
    try:
        assert system.ld2450_capture is not None
        wait_for(lambda: system.ld2450_capture is not None and system.ld2450_capture.read_count > 0)
        recording = system.start_recording(1_000_000_000)
        wait_for(lambda: system.recording_session(recording["session_id"])["record_count"] > 0)
        stopped = system.stop_recording(1_000_000_100)
        assert any(item["kind"] == "RAW_FRAME_V1" for item in system.recording_records(stopped["session_id"]))
        sensors = system.sensor_snapshot(1)
        radar = next(item for item in sensors if item["device_id"] == "ld2450")
        raw_capture = next(item for item in sensors if item["device_id"] == "ld2450_raw_capture")
        assert radar["source_mode"] == "NOT_CONNECTED"
        assert raw_capture["source_mode"] == "NOT_CONNECTED"
        assert "LD2450" in raw_capture["reason"]
        assert system.tick(1_000_000_000)["tracks"] == []
    finally:
        system.close()
    assert captured[0].closed
