from __future__ import annotations
from dataclasses import dataclass
from app.domain.models import RadarDetection
from app.hardware.interfaces import *

@dataclass
class RadarSimulator(RadarInterface):
    scenario: str="TARGET_APPROACH"; active: bool=True
    def read_detections(self, now_ns:int)->list[RadarDetection]:
        if not self.active or self.scenario in {"RADAR_LOSS","RADAR_STALE"}: return []
        if self.scenario=="TARGET_RECEDING": velocity=1.0
        elif self.scenario=="STOP": velocity=-3.0
        else: velocity=-1.0
        items=[RadarDetection(candidate_id=1,x_m=3.0,y_m=.25,velocity_mps=velocity,quality=.9,uncertainty_m=.2,timestamp_ns=now_ns)]
        if self.scenario=="MULTI_TARGET": items.append(RadarDetection(candidate_id=2,x_m=5.0,y_m=-.5,velocity_mps=-.5,quality=.7,uncertainty_m=.5,timestamp_ns=now_ns))
        return items
    def health(self,now_ns:int)->DeviceHealth:
        state="ONLINE" if self.active else "NOT_CONNECTED"; return DeviceHealth("radar","SIMULATION",state,now_ns if self.active else None,0.0 if self.active else None,.9 if self.active else None,f"SIMULATION_{self.scenario}")

class ESP32Simulator(ESP32Interface):
    def __init__(self,connected:bool=True): self.connected=connected
    def status(self,now_ns:int)->DeviceHealth: return DeviceHealth("esp32","SIMULATION","ONLINE" if self.connected else "FAILED",now_ns if self.connected else None,0.0 if self.connected else None,1.0 if self.connected else None,"DISABLED_PHASE_1" if self.connected else "SIMULATED_COMMUNICATION_LOSS")

class EncoderSimulator(EncoderInterface):
    def read_wheel_response(self,now_ns:int)->WheelResponse:return WheelResponse(0.0,0.0,now_ns,"SIMULATION","WHEEL_RESPONSE_SIMULATION_DISABLED_PHASE_1")
class MotorDriverSimulator(MotorDriverInterface):
    def status(self,now_ns:int)->DeviceHealth:return DeviceHealth("mdd10a","SIMULATION","DISABLED_PHASE_1",now_ns,0.0,None,"NO_PHYSICAL_OUTPUT")
class CameraSimulator(CameraInterface):
    def read_frame(self,now_ns:int)->CameraFrame:return CameraFrame(CameraFrameMetadata("vehicle_rgb_camera","SIMULATION","SIMULATION",now_ns,0.0,"UNAVAILABLE",None,"SIMULATED_CAMERA_NO_VIDEO_PAYLOAD"),None,None)
    def health(self,now_ns:int)->DeviceHealth:return DeviceHealth("camera","SIMULATION","SIMULATION",now_ns,0.0,None,"SOFTWARE_INTERFACE_READY_NO_SIMULATED_VIDEO")
class ThermalSimulator(ThermalInterface):
    def read_frame(self,now_ns:int)->ThermalFrame:return ThermalFrame(now_ns,"NOT_CONNECTED_PHASE_2",None,None)
    def health(self,now_ns:int)->DeviceHealth:return DeviceHealth("thermal","NOT_CONNECTED_PHASE_2","NOT_CONNECTED",None,None,None,"SOFTWARE_INTERFACE_READY_FRAME_UNAVAILABLE")
class ImuSimulator(ImuInterface):
    def read_sample(self,now_ns:int)->ImuSample:return ImuSample(now_ns,"NOT_CONNECTED_PHASE_2",None,None,"NOT_CONNECTED_PHASE_2")
    def health(self,now_ns:int)->DeviceHealth:return DeviceHealth("imu","NOT_CONNECTED_PHASE_2","NOT_CONNECTED",None,None,None,"SOFTWARE_INTERFACE_READY_DATA_UNAVAILABLE")

class MDD10AAdapter(MotorDriverInterface):
    """Phase 2 interface reservation: GPIO9/10/11/12 mapping is hardware authority; no physical output here."""
    def status(self,now_ns:int)->DeviceHealth:return DeviceHealth("mdd10a","NOT_CONNECTED_PHASE_2","NOT_CONNECTED",None,None,None,"PHASE_2_HARDWARE_NOT_CONNECTED")
class ESP32EncoderAdapter(EncoderInterface):
    """Phase 2 encoder acquisition boundary; never labels wheel response as ground speed."""
    def read_wheel_response(self,now_ns:int)->WheelResponse:return WheelResponse(None,None,now_ns,"NOT_CONNECTED_PHASE_2","ENCODER_VCC_TBD_VERIFY")
class USBCameraAdapter(CameraInterface):
    """Future Pi/UVC source: frame transport is intentionally not JSON or browser-camera upload."""
    def read_frame(self,now_ns:int)->CameraFrame:return CameraFrame(CameraFrameMetadata("vehicle_rgb_camera","NOT_CONNECTED_PHASE_2","NOT_CONNECTED",None,None,None,None,"PI_UVC_CAMERA_NOT_CONNECTED"),None,None)
    def health(self,now_ns:int)->DeviceHealth:return DeviceHealth("camera","NOT_CONNECTED_PHASE_2","NOT_CONNECTED",None,None,None,"SOFTWARE_INTERFACE_READY_PI_UVC_CAMERA_PENDING")
class MLX90640Adapter(ThermalInterface):
    def read_frame(self,now_ns:int)->ThermalFrame:return ThermalFrame(now_ns,"NOT_CONNECTED_PHASE_2",None,None)
    def health(self,now_ns:int)->DeviceHealth:return DeviceHealth("thermal","NOT_CONNECTED_PHASE_2","NOT_CONNECTED",None,None,None,"SOFTWARE_INTERFACE_READY_MLX90640_PENDING")
class BNO055Adapter(ImuInterface):
    def read_sample(self,now_ns:int)->ImuSample:return ImuSample(now_ns,"NOT_CONNECTED_PHASE_2",None,None,"NOT_CONNECTED_PHASE_2")
    def health(self,now_ns:int)->DeviceHealth:return DeviceHealth("imu","NOT_CONNECTED_PHASE_2","NOT_CONNECTED",None,None,None,"SOFTWARE_INTERFACE_READY_BNO055_PENDING")
