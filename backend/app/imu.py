"""BNO055 boundary; optional hardware libraries start only after identity verification."""
from __future__ import annotations
import math, os, threading, time
from dataclasses import dataclass
from typing import Any, Protocol
from app.hardware.interfaces import DeviceHealth, ImuSample, ImuInterface
from app.i2c_transport import I2cSensorWorker, I2cTransport
from app.sensor_identity import DeviceIdentity

@dataclass(frozen=True)
class ImuConfig:
    bus:int=1; address:str=""; sample_hz:float=20; stale_ms:int=1500; reconnect_s:float=.5
    @classmethod
    def from_environment(cls)->"ImuConfig":
        def number(name,default):
            try:return float(os.getenv(name,str(default)))
            except ValueError:return default
        return cls(int(number("TARK_IMU_I2C_BUS",1)),os.getenv("TARK_IMU_I2C_ADDRESS","").strip(),number("TARK_IMU_SAMPLE_HZ",20),int(number("TARK_IMU_STALE_MS",1500)),number("TARK_IMU_RECONNECT_INTERVAL_S",.5))
    @property
    def address_value(self)->int|None:
        try:return int(self.address,0) if self.address else None
        except ValueError:return None


class Bno055Sensor(Protocol):
    """The optional Adafruit driver's documented data-property surface."""
    euler: tuple[float | None, float | None, float | None] | None
    quaternion: tuple[float | None, float | None, float | None, float | None] | None
    linear_acceleration: tuple[float | None, float | None, float | None] | None
    gyro: tuple[float | None, float | None, float | None] | None
    calibration_status: tuple[int, int, int, int] | None


def create_bno055_sensor(config: ImuConfig) -> Bno055Sensor:
    """Create the optional-library sensor only for an already-verified device.

    This factory is intentionally called by ``TarkSystem`` only after its
    adapter has recorded external identity evidence.  Configuration identifies
    a candidate; it is not identity evidence and cannot trigger this factory.
    """
    if config.address_value is None:
        raise ImuAcquisitionError("BNO055 I2C address is not configured")
    try:
        import adafruit_bno055
        import board
        import busio
    except ImportError as error:
        raise ImuAcquisitionError("BNO055 optional library is unavailable") from error
    try:
        return adafruit_bno055.BNO055_I2C(
            busio.I2C(board.SCL, board.SDA), address=config.address_value
        )
    except Exception as error:
        raise ImuAcquisitionError(f"BNO055 startup failed: {type(error).__name__}") from error


class ImuAcquisitionError(RuntimeError):
    """A malformed or unavailable library sample; never a replacement value."""


def _finite_tuple(value: Any, length: int, field: str) -> tuple[float, ...]:
    if not isinstance(value, (tuple, list)) or len(value) != length:
        raise ImuAcquisitionError(f"BNO055 {field} is unavailable or malformed")
    try:
        normalized = tuple(float(item) for item in value)
    except (TypeError, ValueError) as error:
        raise ImuAcquisitionError(f"BNO055 {field} is unavailable or malformed") from error
    if not all(math.isfinite(item) for item in normalized):
        raise ImuAcquisitionError(f"BNO055 {field} contains a non-finite value")
    return normalized


class Bno055SampleReader:
    """Concrete, injectable read-once acquisition against the optional library.

    It uses only the documented euler/quaternion/linear_acceleration/gyro and
    calibration properties.  Mounting orientation is not known yet, so the
    project does not infer a vehicle-axis angular rate from the gyro vector.
    """
    def __init__(self, sensor: Bno055Sensor): self.sensor = sensor

    def read_once(self) -> ImuSample:
        try:
            euler = _finite_tuple(self.sensor.euler, 3, "euler")
            quaternion = _finite_tuple(self.sensor.quaternion, 4, "quaternion")
            acceleration = _finite_tuple(self.sensor.linear_acceleration, 3, "linear acceleration")
            gyro = _finite_tuple(self.sensor.gyro, 3, "gyro")
            calibration = self.sensor.calibration_status
        except ImuAcquisitionError:
            raise
        except Exception as error:
            raise ImuAcquisitionError(f"BNO055 library read failed: {type(error).__name__}") from error
        calibrated = isinstance(calibration, (tuple, list)) and len(calibration) == 4 and all(item == 3 for item in calibration)
        return ImuSample(
            timestamp_ns=time.monotonic_ns(), source_mode="PI_I2C",
            yaw_deg=euler[0], angular_rate_dps=None,
            calibration="CALIBRATED" if calibrated else "UNCALIBRATED",
            state="ONLINE", quaternion=quaternion,
            linear_acceleration_mps2=acceleration, angular_velocity_radps=gyro,
            quality=None, reason="BNO055 LIBRARY SAMPLE",
        )

class Bno055Adapter(ImuInterface):
    def __init__(self,config:ImuConfig|None=None,transport:I2cTransport|None=None):
        self.config=config or ImuConfig.from_environment();self.transport=transport or I2cTransport(self.config.bus,self.config.address_value);self.identity=DeviceIdentity("I2C",f"bus={self.config.bus};address={self.config.address or 'UNSET'}",state="UNVERIFIED",evidence_source="CONFIGURATION_ONLY");self.worker:I2cSensorWorker|None=None;self._sample:ImuSample|None=None;self._state="NOT_CONNECTED";self._reason="BNO055 I2C ADDRESS NOT CONFIGURED" if not self.config.address else "I2C DEVICE CONFIGURED; IDENTITY UNVERIFIED";self._sequence=0;self._lock=threading.Lock()
    def discover(self)->dict:return {"state":"NOT_CONNECTED" if not self.config.address else "DISCOVERED","bus":self.config.bus,"address":self.config.address or None,"identity":self.identity.state,"verification_source":self.identity.evidence_source}
    def record_verified_identity(self,evidence_source:str,chip_id:str|None=None)->None:self.identity=DeviceIdentity(**{**self.identity.__dict__,"chip_id":chip_id}).verified(evidence_source)
    def report_startup_error(self, error: Exception) -> None:
        """Expose a configured reader-startup failure without inventing data."""
        self._state="ERROR";self._reason=f"BNO055 STARTUP ERROR: {type(error).__name__}"
    def start_verified_worker(self,read_once)->bool:
        if self.identity.state!="VERIFIED":self._state="DISCOVERED";self._reason="BNO055 IDENTITY UNVERIFIED";return False
        def guarded_read_once():
            try:return read_once()
            except Exception as error:
                self._state="ERROR";self._reason=f"BNO055 READ ERROR: {type(error).__name__}";raise
        self.worker=I2cSensorWorker(guarded_read_once,self.accept,1/max(.1,self.config.sample_hz),self.config.reconnect_s);return self.worker.start()
    def start_verified_sensor(self,sensor:Bno055Sensor)->bool:
        """Start an already-created, identity-verified optional-library sensor."""
        return self.start_verified_worker(Bno055SampleReader(sensor).read_once)
    def stop(self)->None:
        if self.worker:self.worker.stop();self.worker=None
        self.transport.close()
    def accept(self,sample:ImuSample)->bool:
        values=(sample.quaternion or ())+(sample.linear_acceleration_mps2 or ())+(sample.angular_velocity_radps or ())
        if not values or not all(math.isfinite(value) for value in values):self._state="ERROR";self._reason="INVALID IMU SAMPLE";return False
        if len(sample.quaternion or ())!=4:self._state="ERROR";self._reason="INVALID IMU QUATERNION";return False
        self._sequence+=1;self._sample=ImuSample(**{**sample.__dict__,"sequence":self._sequence});self._state="ONLINE";self._reason="IMU SAMPLE ACCEPTED";return True
    def inject_simulation(self,now_ns:int|None=None,yaw_deg:float=0.0)->None:
        now=now_ns or time.monotonic_ns();self.accept(ImuSample(now,"SIMULATION",yaw_deg,0.0,"UNCALIBRATED",state="ONLINE",quaternion=(1.0,0.0,0.0,0.0),linear_acceleration_mps2=(0.0,0.0,0.0),angular_velocity_radps=(0.0,0.0,0.0),quality=1.0,reason="SIMULATION"))
    def read_sample(self,now_ns:int)->ImuSample:
        sample=self._sample
        if not sample:return ImuSample(now_ns,"NOT_CONNECTED_PHASE_2",None,None,"UNKNOWN",state=self._state,reason=self._reason)
        if self._state=="ERROR":return ImuSample(**{**sample.__dict__,"state":"ERROR","reason":self._reason})
        if (now_ns-sample.timestamp_ns)/1e6>self.config.stale_ms:return ImuSample(**{**sample.__dict__,"state":"STALE","reason":"IMU SAMPLE STALE"})
        return sample
    def health(self,now_ns:int)->DeviceHealth:
        sample=self.read_sample(now_ns);age=None if self._sample is None else max(0.0,(now_ns-self._sample.timestamp_ns)/1e6);return DeviceHealth("imu",sample.source_mode,sample.state,self._sample.timestamp_ns if self._sample else None,age,sample.quality,sample.reason)
