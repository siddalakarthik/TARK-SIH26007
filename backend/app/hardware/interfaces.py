from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal
from app.domain.models import RadarDetection

SourceMode = Literal["SIMULATION", "REPLAY", "REAL_HARDWARE", "NOT_CONNECTED_PHASE_2", "PI_UVC", "PI_I2C", "BROWSER_PREVIEW", "UNKNOWN"]

@dataclass(frozen=True)
class DeviceHealth:
    device_id: str; source_mode: SourceMode; state: str; timestamp_ns: int | None; age_ms: float | None; quality: float | None; reason: str

@dataclass(frozen=True)
class WheelResponse:
    left_mps: float | None; right_mps: float | None; timestamp_ns: int; source_mode: SourceMode; reason: str

@dataclass(frozen=True)
class CameraFrameMetadata:
    source_id: str; source_mode: SourceMode; state: str; timestamp_ns: int | None; age_ms: float | None; resolution: str | None; frame_rate_fps: float | None; reason: str
    camera_id: str | None = None; device_path: str | None = None; pixel_format: str | None = None; sequence: int | None = None; dropped_frames: int = 0; backend: str | None = None

@dataclass(frozen=True)
class CameraFrame:
    metadata: CameraFrameMetadata; quality: float | None; payload: bytes | None

@dataclass(frozen=True)
class ThermalFrame:
    timestamp_ns: int; source_mode: SourceMode; temperatures_c: tuple[float, ...] | None; quality: float | None
    state: str = "NOT_CONNECTED"; sequence: int = 0; width: int = 32; height: int = 24; reason: str = "NOT_CONNECTED"; invalid_pixels: int = 0

@dataclass(frozen=True)
class ImuSample:
    timestamp_ns: int; source_mode: SourceMode; yaw_deg: float | None; angular_rate_dps: float | None; calibration: str
    state: str = "NOT_CONNECTED"; sequence: int = 0; quaternion: tuple[float,float,float,float] | None = None; linear_acceleration_mps2: tuple[float,float,float] | None = None; angular_velocity_radps: tuple[float,float,float] | None = None; temperature_c: float | None = None; quality: float | None = None; reason: str = "NOT_CONNECTED"

class RadarInterface(ABC):
    @abstractmethod
    def read_detections(self, now_ns: int) -> list[RadarDetection]: ...
    @abstractmethod
    def health(self, now_ns: int) -> DeviceHealth: ...

class ESP32Interface(ABC):
    @abstractmethod
    def status(self, now_ns: int) -> DeviceHealth: ...

class EncoderInterface(ABC):
    @abstractmethod
    def read_wheel_response(self, now_ns: int) -> WheelResponse: ...

class MotorDriverInterface(ABC):
    @abstractmethod
    def status(self, now_ns: int) -> DeviceHealth: ...

class CameraInterface(ABC):
    @abstractmethod
    def read_frame(self, now_ns: int) -> CameraFrame: ...
    @abstractmethod
    def health(self, now_ns: int) -> DeviceHealth: ...

class ThermalInterface(ABC):
    @abstractmethod
    def read_frame(self, now_ns: int) -> ThermalFrame: ...
    @abstractmethod
    def health(self, now_ns: int) -> DeviceHealth: ...

class ImuInterface(ABC):
    @abstractmethod
    def read_sample(self, now_ns: int) -> ImuSample: ...
    @abstractmethod
    def health(self, now_ns: int) -> DeviceHealth: ...
