"""Deterministic optional-library acquisition tests; no I²C bus is opened."""
from __future__ import annotations

import time

import pytest

from app.imu import Bno055Adapter, Bno055SampleReader, ImuAcquisitionError, ImuConfig
from app.thermal import Mlx90640Adapter, Mlx90640FrameReader, ThermalAcquisitionError, ThermalConfig


class FakeBno055:
    euler = (45.0, 1.0, -2.0)
    quaternion = (1.0, 0.0, 0.0, 0.0)
    linear_acceleration = (0.1, 0.2, 0.3)
    gyro = (0.01, 0.02, 0.03)
    calibration_status = (3, 3, 3, 3)


class FakeMlx90640:
    def getFrame(self, frame):
        for index in range(768):
            frame[index] = 20.0 + (index % 3)


def wait_for(predicate):
    for _ in range(100):
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError("worker did not reach expected state")


def test_bno055_reader_normalizes_documented_properties_without_inventing_axis_rate():
    sample = Bno055SampleReader(FakeBno055()).read_once()
    assert sample.source_mode == "PI_I2C" and sample.state == "ONLINE"
    assert sample.yaw_deg == 45.0 and sample.angular_rate_dps is None
    assert sample.quaternion == (1.0, 0.0, 0.0, 0.0)
    assert sample.linear_acceleration_mps2 == (0.1, 0.2, 0.3)
    assert sample.angular_velocity_radps == (0.01, 0.02, 0.03)
    assert sample.calibration == "CALIBRATED"


def test_bno055_reader_rejects_malformed_and_exceptional_samples():
    malformed = FakeBno055(); malformed.quaternion = (1.0, 0.0)
    with pytest.raises(ImuAcquisitionError): Bno055SampleReader(malformed).read_once()
    class Broken:
        @property
        def euler(self): raise OSError("fixture")
    with pytest.raises(ImuAcquisitionError): Bno055SampleReader(Broken()).read_once()


def test_bno055_adapter_is_unavailable_until_identity_then_reports_worker_errors():
    adapter = Bno055Adapter(ImuConfig(address="0x28", sample_hz=100, reconnect_s=.01))
    assert adapter.read_sample(1).state == "NOT_CONNECTED"
    assert not adapter.start_verified_sensor(FakeBno055())
    adapter.record_verified_identity("test fixture")
    assert adapter.start_verified_sensor(FakeBno055())
    try:
        wait_for(lambda: adapter.health(time.monotonic_ns()).state == "ONLINE")
    finally:
        adapter.stop()
    class BrokenReader:
        def read_once(self): raise OSError("fixture")
    adapter.record_verified_identity("test fixture")
    assert adapter.start_verified_worker(BrokenReader().read_once)
    try:
        wait_for(lambda: adapter.health(time.monotonic_ns()).state == "ERROR")
    finally:
        adapter.stop()


def test_mlx90640_reader_normalizes_768_temperature_values_and_rejects_errors():
    values = Mlx90640FrameReader(FakeMlx90640()).read_once()
    assert len(values) == 768 and min(values) == 20.0 and max(values) == 22.0
    class Malformed:
        def getFrame(self, frame): frame[0] = float("nan")
    with pytest.raises(ThermalAcquisitionError): Mlx90640FrameReader(Malformed()).read_once()
    class Broken:
        def getFrame(self, frame): raise OSError("fixture")
    with pytest.raises(ThermalAcquisitionError): Mlx90640FrameReader(Broken()).read_once()


def test_mlx90640_adapter_is_unavailable_until_identity_then_reports_worker_errors():
    adapter = Mlx90640Adapter(ThermalConfig(address="0x33", sample_hz=100, reconnect_s=.01))
    assert adapter.read_frame(1).state == "NOT_CONNECTED"
    assert not adapter.start_verified_sensor(FakeMlx90640())
    adapter.record_verified_identity("test fixture")
    assert adapter.start_verified_sensor(FakeMlx90640())
    try:
        wait_for(lambda: adapter.health(time.monotonic_ns()).state == "ONLINE")
        frame = adapter.read_frame(time.monotonic_ns())
        assert frame.temperatures_c is not None and min(frame.temperatures_c) == 20.0 and max(frame.temperatures_c) == 22.0
    finally:
        adapter.stop()
    class BrokenReader:
        def read_once(self): raise OSError("fixture")
    adapter.record_verified_identity("test fixture")
    assert adapter.start_verified_worker(BrokenReader().read_once)
    try:
        wait_for(lambda: adapter.health(time.monotonic_ns()).state == "ERROR")
    finally:
        adapter.stop()
