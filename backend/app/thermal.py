"""MLX90640 boundary. Low-level register/library behaviour remains hardware verification work."""
from __future__ import annotations
import math, os, time
from dataclasses import dataclass
from typing import Any, Protocol
from app.hardware.interfaces import DeviceHealth, ThermalFrame, ThermalInterface
from app.i2c_transport import I2cSensorWorker, I2cTransport
from app.sensor_identity import DeviceIdentity

@dataclass(frozen=True)
class ThermalConfig:
    bus:int=1;address:str="";sample_hz:float=8;stale_ms:int=2000;reconnect_s:float=.5
    @classmethod
    def from_environment(cls)->"ThermalConfig":
        def number(name,default):
            try:return float(os.getenv(name,str(default)))
            except ValueError:return default
        return cls(int(number("TARK_THERMAL_I2C_BUS",1)),os.getenv("TARK_THERMAL_I2C_ADDRESS","").strip(),number("TARK_THERMAL_SAMPLE_HZ",8),int(number("TARK_THERMAL_STALE_MS",2000)),number("TARK_THERMAL_RECONNECT_INTERVAL_S",.5))
    @property
    def address_value(self)->int|None:
        try:return int(self.address,0) if self.address else None
        except ValueError:return None


class Mlx90640Sensor(Protocol):
    """The documented optional-library frame acquisition surface."""
    def getFrame(self, framebuf: list[float]) -> None: ...


def create_mlx90640_sensor(config: ThermalConfig) -> Mlx90640Sensor:
    """Create the optional-library sensor only for an already-verified device."""
    if config.address_value is None:
        raise ThermalAcquisitionError("MLX90640 I2C address is not configured")
    try:
        import adafruit_mlx90640
        import board
        import busio
    except ImportError as error:
        raise ThermalAcquisitionError("MLX90640 optional library is unavailable") from error
    try:
        return adafruit_mlx90640.MLX90640(
            busio.I2C(board.SCL, board.SDA), address=config.address_value
        )
    except Exception as error:
        raise ThermalAcquisitionError(f"MLX90640 startup failed: {type(error).__name__}") from error


class ThermalAcquisitionError(RuntimeError):
    """A failed library frame acquisition; never a fabricated temperature grid."""


class Mlx90640FrameReader:
    """Concrete, injectable 32×24 frame reader for the optional library."""
    def __init__(self, sensor: Mlx90640Sensor): self.sensor = sensor

    def read_once(self) -> tuple[float, ...]:
        frame: list[float] = [float("nan")] * 768
        try:
            self.sensor.getFrame(frame)
        except Exception as error:
            raise ThermalAcquisitionError(f"MLX90640 library read failed: {type(error).__name__}") from error
        try:
            normalized = tuple(float(value) for value in frame)
        except (TypeError, ValueError) as error:
            raise ThermalAcquisitionError("MLX90640 frame is malformed") from error
        if len(normalized) != 768 or not all(math.isfinite(value) for value in normalized):
            raise ThermalAcquisitionError("MLX90640 frame is malformed")
        return normalized

class Mlx90640Adapter(ThermalInterface):
    def __init__(self,config:ThermalConfig|None=None,transport:I2cTransport|None=None):
        self.config=config or ThermalConfig.from_environment();self.transport=transport or I2cTransport(self.config.bus,self.config.address_value);self.identity=DeviceIdentity("I2C",f"bus={self.config.bus};address={self.config.address or 'UNSET'}",state="UNVERIFIED",evidence_source="CONFIGURATION_ONLY");self.worker:I2cSensorWorker|None=None;self._frame:ThermalFrame|None=None;self._state="NOT_CONNECTED";self._reason="MLX90640 I2C ADDRESS NOT CONFIGURED" if not self.config.address else "I2C DEVICE CONFIGURED; IDENTITY UNVERIFIED";self._sequence=0
    def discover(self)->dict:return {"state":"NOT_CONNECTED" if not self.config.address else "DISCOVERED","bus":self.config.bus,"address":self.config.address or None,"identity":self.identity.state,"verification_source":self.identity.evidence_source}
    def record_verified_identity(self,evidence_source:str,chip_id:str|None=None)->None:self.identity=DeviceIdentity(**{**self.identity.__dict__,"chip_id":chip_id}).verified(evidence_source)
    def report_startup_error(self, error: Exception) -> None:
        """Expose a configured reader-startup failure without fabricating a frame."""
        self._state="ERROR";self._reason=f"MLX90640 STARTUP ERROR: {type(error).__name__}"
    def start_verified_worker(self,read_once)->bool:
        if self.identity.state!="VERIFIED":self._state="DISCOVERED";self._reason="MLX90640 IDENTITY UNVERIFIED";return False
        def guarded_read_once():
            try:return read_once()
            except Exception as error:
                self._state="ERROR";self._reason=f"MLX90640 READ ERROR: {type(error).__name__}";raise
        self.worker=I2cSensorWorker(guarded_read_once,lambda values:self.accept(tuple(values),source="PI_I2C"),1/max(.1,self.config.sample_hz),self.config.reconnect_s);return self.worker.start()
    def start_verified_sensor(self,sensor:Mlx90640Sensor)->bool:
        """Start an already-created, identity-verified optional-library sensor."""
        return self.start_verified_worker(Mlx90640FrameReader(sensor).read_once)
    def stop(self)->None:
        if self.worker:self.worker.stop();self.worker=None
        self.transport.close()
    def accept(self,values:tuple[float,...],timestamp_ns:int|None=None,source:str="SIMULATION")->bool:
        if len(values)!=768 or not all(math.isfinite(value) for value in values):self._state="ERROR";self._reason="INVALID THERMAL FRAME";return False
        self._sequence+=1;now=timestamp_ns or time.monotonic_ns();self._frame=ThermalFrame(now,source,values,1.0,state="ONLINE",sequence=self._sequence,width=32,height=24,reason="THERMAL FRAME ACCEPTED");self._state="ONLINE";self._reason="THERMAL FRAME ACCEPTED";return True
    def inject_simulation(self,now_ns:int|None=None,warm_index:int=384)->None:
        values=[22.0]*768;values[max(0,min(767,warm_index))]=36.0;self.accept(tuple(values),now_ns,"SIMULATION")
    def read_frame(self,now_ns:int)->ThermalFrame:
        if not self._frame:return ThermalFrame(now_ns,"NOT_CONNECTED_PHASE_2",None,None,state=self._state,reason=self._reason)
        if self._state=="ERROR":return ThermalFrame(**{**self._frame.__dict__,"state":"ERROR","reason":self._reason})
        if (now_ns-self._frame.timestamp_ns)/1e6>self.config.stale_ms:return ThermalFrame(**{**self._frame.__dict__,"state":"STALE","reason":"THERMAL FRAME STALE"})
        return self._frame
    def health(self,now_ns:int)->DeviceHealth:
        frame=self.read_frame(now_ns);age=None if self._frame is None else max(0.0,(now_ns-self._frame.timestamp_ns)/1e6);return DeviceHealth("thermal",frame.source_mode,frame.state,self._frame.timestamp_ns if self._frame else None,age,frame.quality,frame.reason)
