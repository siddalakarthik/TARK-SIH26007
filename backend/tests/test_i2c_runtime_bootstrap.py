"""TarkSystem I²C bootstrap tests use injected readers only; no bus is opened."""
from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import Mock

from app.config import Settings
from app.imu import Bno055Adapter, ImuConfig
from app.services.system import TarkSystem
from app.thermal import Mlx90640Adapter, ThermalConfig


ROOT = Path(__file__).parents[2]


def real_settings() -> Settings:
    return Settings.from_file(ROOT / "config" / "phase1.json").model_copy(update={"mode": "real_radar"})


def wait_for(predicate, message: str = "worker did not reach expected state") -> None:
    for _ in range(100):
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError(message)


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


def test_i2c_bootstrap_leaves_unconfigured_adapters_inactive(monkeypatch, tmp_path):
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "tark.db"))
    imu_factory = Mock()
    thermal_factory = Mock()
    system = TarkSystem(
        real_settings(),
        imu=Bno055Adapter(ImuConfig(address="")),
        thermal=Mlx90640Adapter(ThermalConfig(address="")),
        imu_sensor_factory=imu_factory,
        thermal_sensor_factory=thermal_factory,
    )
    try:
        assert system.imu.worker is None and system.thermal.worker is None
        assert system.imu.health(time.monotonic_ns()).state == "NOT_CONNECTED"
        assert system.thermal.health(time.monotonic_ns()).state == "NOT_CONNECTED"
        imu_factory.assert_not_called()
        thermal_factory.assert_not_called()
    finally:
        system.close()


def test_i2c_bootstrap_keeps_configured_unverified_candidates_inactive(monkeypatch, tmp_path):
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "tark.db"))
    imu_factory = Mock()
    thermal_factory = Mock()
    system = TarkSystem(
        real_settings(),
        imu=Bno055Adapter(ImuConfig(address="0x28")),
        thermal=Mlx90640Adapter(ThermalConfig(address="0x33")),
        imu_sensor_factory=imu_factory,
        thermal_sensor_factory=thermal_factory,
    )
    try:
        assert system.imu.health(time.monotonic_ns()).state == "NOT_CONNECTED"
        assert system.thermal.health(time.monotonic_ns()).state == "NOT_CONNECTED"
        imu_factory.assert_not_called()
        thermal_factory.assert_not_called()
    finally:
        system.close()


def test_i2c_bootstrap_reports_configured_reader_startup_failures(monkeypatch, tmp_path):
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "tark.db"))
    imu = Bno055Adapter(ImuConfig(address="0x28"))
    thermal = Mlx90640Adapter(ThermalConfig(address="0x33"))
    imu.record_verified_identity("test fixture")
    thermal.record_verified_identity("test fixture")
    system = TarkSystem(
        real_settings(), imu=imu, thermal=thermal,
        imu_sensor_factory=Mock(side_effect=OSError("unavailable")),
        thermal_sensor_factory=Mock(side_effect=OSError("unavailable")),
    )
    try:
        assert imu.health(time.monotonic_ns()).state == "ERROR"
        assert thermal.health(time.monotonic_ns()).state == "ERROR"
        assert "STARTUP ERROR" in imu.health(time.monotonic_ns()).reason
        assert "STARTUP ERROR" in thermal.health(time.monotonic_ns()).reason
    finally:
        system.close()


def test_i2c_bootstrap_starts_mocked_readers_and_publishes_normalized_samples(monkeypatch, tmp_path):
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "tark.db"))
    imu = Bno055Adapter(ImuConfig(address="0x28", sample_hz=100, reconnect_s=.01))
    thermal = Mlx90640Adapter(ThermalConfig(address="0x33", sample_hz=100, reconnect_s=.01))
    imu.record_verified_identity("test fixture")
    thermal.record_verified_identity("test fixture")
    system = TarkSystem(
        real_settings(), imu=imu, thermal=thermal,
        imu_sensor_factory=Mock(return_value=FakeBno055()),
        thermal_sensor_factory=Mock(return_value=FakeMlx90640()),
    )
    try:
        wait_for(lambda: imu.health(time.monotonic_ns()).state == "ONLINE")
        wait_for(lambda: thermal.health(time.monotonic_ns()).state == "ONLINE")
        sample = imu.read_sample(time.monotonic_ns())
        frame = thermal.read_frame(time.monotonic_ns())
        assert sample.source_mode == "PI_I2C" and sample.yaw_deg == 45.0
        assert frame.source_mode == "PI_I2C" and frame.temperatures_c is not None
        assert min(frame.temperatures_c) == 20.0 and max(frame.temperatures_c) == 22.0
    finally:
        system.close()
    assert imu.worker is None and thermal.worker is None


def test_i2c_bootstrap_reader_failures_remain_error_states(monkeypatch, tmp_path):
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "tark.db"))

    class BrokenBno055:
        @property
        def euler(self):
            raise OSError("fixture")

    class BrokenMlx90640:
        def getFrame(self, _frame):
            raise OSError("fixture")

    imu = Bno055Adapter(ImuConfig(address="0x28", sample_hz=100, reconnect_s=.01))
    thermal = Mlx90640Adapter(ThermalConfig(address="0x33", sample_hz=100, reconnect_s=.01))
    imu.record_verified_identity("test fixture")
    thermal.record_verified_identity("test fixture")
    system = TarkSystem(
        real_settings(), imu=imu, thermal=thermal,
        imu_sensor_factory=lambda _config: BrokenBno055(),
        thermal_sensor_factory=lambda _config: BrokenMlx90640(),
    )
    try:
        wait_for(lambda: imu.health(time.monotonic_ns()).state == "ERROR")
        wait_for(lambda: thermal.health(time.monotonic_ns()).state == "ERROR")
        assert "READ ERROR" in imu.health(time.monotonic_ns()).reason
        assert "READ ERROR" in thermal.health(time.monotonic_ns()).reason
    finally:
        system.close()


def test_verified_i2c_sensors_can_start_after_runtime_construction(monkeypatch, tmp_path):
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "tark.db"))
    imu = Bno055Adapter(ImuConfig(address="0x28", sample_hz=100, reconnect_s=.01))
    thermal = Mlx90640Adapter(ThermalConfig(address="0x33", sample_hz=100, reconnect_s=.01))
    system = TarkSystem(
        real_settings(), imu=imu, thermal=thermal,
        imu_sensor_factory=lambda _config: FakeBno055(),
        thermal_sensor_factory=lambda _config: FakeMlx90640(),
    )
    try:
        assert system.start_verified_configured_i2c_sensors() == {"imu": False, "thermal": False}
        imu.record_verified_identity("test fixture")
        thermal.record_verified_identity("test fixture")
        assert system.start_verified_configured_i2c_sensors() == {"imu": True, "thermal": True}
        wait_for(lambda: imu.health(time.monotonic_ns()).state == "ONLINE")
        wait_for(lambda: thermal.health(time.monotonic_ns()).state == "ONLINE")
    finally:
        system.close()
