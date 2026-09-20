"""Dormant Pi/UVC capture boundary. It is observation-only and never starts automatically."""
from __future__ import annotations
import os, threading, time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from app.hardware.interfaces import CameraFrame, CameraFrameMetadata, CameraInterface, DeviceHealth
from app.sensor_identity import DeviceIdentity

@dataclass(frozen=True)
class CameraConfig:
    device_path: str = ""; preferred_width: int = 1280; preferred_height: int = 720; preferred_fps: float = 30; stale_ms: int = 3000; stream_fps: float = 10; jpeg_quality: int = 80; failure_threshold:int=5; reconnect_s:float=1.0
    @classmethod
    def from_environment(cls)->"CameraConfig":
        def integer(name:str,default:int)->int:
            try:return int(os.getenv(name,str(default)))
            except ValueError:return default
        def number(name:str,default:float)->float:
            try:return float(os.getenv(name,str(default)))
            except ValueError:return default
        return cls(os.getenv("TARK_CAMERA_DEVICE_PATH","").strip(),integer("TARK_CAMERA_WIDTH",1280),integer("TARK_CAMERA_HEIGHT",720),number("TARK_CAMERA_FPS",30),integer("TARK_CAMERA_STALE_MS",3000),number("TARK_CAMERA_STREAM_FPS",10),integer("TARK_CAMERA_JPEG_QUALITY",80),integer("TARK_CAMERA_FAILURE_THRESHOLD",5),number("TARK_CAMERA_RECONNECT_INTERVAL_S",1))

def discover_uvc_candidates(path_override:str="")->list[dict[str,str|bool]]:
    if path_override:return [{"path":path_override,"identity":"UNVERIFIED","selected":True}]
    root=Path("/dev")
    return [{"path":str(path),"identity":"UNVERIFIED","selected":False} for path in sorted(root.glob("video*"))] if root.exists() else []

class PiUvcCameraAdapter(CameraInterface):
    def __init__(self, config:CameraConfig|None=None, cv2_module:Any|None=None):
        self.config=config or CameraConfig.from_environment();self.identity=DeviceIdentity("UVC",self.config.device_path or "UNSET",state="UNVERIFIED",evidence_source="CONFIGURATION_ONLY");self._cv2=cv2_module;self._capture:Any=None;self._thread:threading.Thread|None=None;self._stop=threading.Event();self._lock=threading.Lock();self._latest:tuple[CameraFrameMetadata,bytes]|None=None;self._state="NOT_CONNECTED";self._reason="PI UVC CAMERA NOT CONFIGURED" if not self.config.device_path else "DEVICE CONFIGURED; IDENTITY UNVERIFIED";self._sequence=0;self._dropped=0;self._reconnects=0;self._failures=0
    def discover(self)->dict:
        candidates=discover_uvc_candidates(self.config.device_path)
        return {"state":"NO_CAMERA" if not candidates else "DEVICE_DETECTED","candidates":candidates,"identity":self.identity.state,"verification_source":self.identity.evidence_source}
    def record_verified_identity(self,evidence_source:str,**facts:str|None)->None:self.identity=DeviceIdentity(**{**self.identity.__dict__,**facts}).verified(evidence_source)
    def start(self)->bool:
        # A caller must stop/acknowledge a failed worker before retrying; this
        # prevents an open failure race from spawning overlapping readers.
        if self._thread is not None:return False
        if not self.config.device_path:self._state="NOT_CONNECTED";self._reason="PI UVC CAMERA NOT CONFIGURED";return False
        self._stop.clear();self._thread=threading.Thread(target=self._run,name="tark-pi-uvc-camera",daemon=True);self._thread.start();return True
    def stop(self)->None:
        self._stop.set()
        if self._thread:self._thread.join(timeout=2)
        self._thread=None
        if self._capture:
            try:self._capture.release()
            except Exception:pass
        self._capture=None
        with self._lock:self._latest=None
        # An explicit lifecycle shutdown is truthful ``NOT_CONNECTED`` even if
        # the previous worker failure was retained as diagnostics.  It prevents
        # a stale error from looking like an actively connected capture path.
        self._state="NOT_CONNECTED";self._reason="PI UVC CAMERA STOPPED"
    def _load_cv2(self)->Any:
        if self._cv2 is not None:return self._cv2
        import cv2
        self._cv2=cv2;return cv2
    def _run(self)->None:
        cv2=self._load_cv2()
        while not self._stop.is_set():
            capture=None
            try:
                self._state="OPENING";capture=cv2.VideoCapture(self.config.device_path);self._capture=capture
                if not capture.isOpened():raise OSError("camera open failed")
                capture.set(cv2.CAP_PROP_FRAME_WIDTH,self.config.preferred_width);capture.set(cv2.CAP_PROP_FRAME_HEIGHT,self.config.preferred_height);capture.set(cv2.CAP_PROP_FPS,self.config.preferred_fps);self._failures=0
                while not self._stop.is_set():
                    ok,image=capture.read()
                    if not ok or image is None:
                        self._dropped+=1;self._failures+=1;self._state="DROPPED";self._reason="CAMERA FRAME READ FAILED"
                        if self._failures>=max(1,self.config.failure_threshold):raise OSError("camera failure threshold reached")
                        if self._stop.wait(.02):break
                        continue
                    ok,jpeg=cv2.imencode(".jpg",image,[int(cv2.IMWRITE_JPEG_QUALITY),max(1,min(100,self.config.jpeg_quality))])
                    if not ok:self._dropped+=1;continue
                    now=time.monotonic_ns();height,width=image.shape[:2];fps=capture.get(cv2.CAP_PROP_FPS) or None;self._sequence+=1;self._failures=0
                    meta=CameraFrameMetadata("vehicle_rgb_camera","PI_UVC","ONLINE",now,0.0,f"{width}x{height}",float(fps) if fps else None,"PI UVC FRAME",camera_id="vehicle_rgb_camera",device_path=self.config.device_path,pixel_format="JPEG",sequence=self._sequence,dropped_frames=self._dropped,backend="OpenCV/V4L2")
                    with self._lock:self._latest=(meta,bytes(jpeg))
                    self._state="ONLINE";self._reason="PI UVC STREAM ACTIVE"
            except Exception as error:
                self._state="ERROR";self._reason=f"CAMERA ERROR: {type(error).__name__}";self._reconnects+=1
            finally:
                if capture:
                    try:capture.release()
                    except Exception:pass
                self._capture=None
            if not self._stop.wait(max(.1,self.config.reconnect_s)):continue
    def inject_frame_for_test(self,payload:bytes,width:int=640,height:int=480,fps:float=10.0)->None:
        """Test fixture only; callers must label their source externally, never real PI UVC."""
        now=time.monotonic_ns();self._sequence+=1;meta=CameraFrameMetadata("vehicle_rgb_camera","SIMULATION","ONLINE",now,0.0,f"{width}x{height}",fps,"TEST FIXTURE FRAME",camera_id="vehicle_rgb_camera",device_path=self.config.device_path or None,pixel_format="JPEG",sequence=self._sequence,dropped_frames=self._dropped,backend="TEST_FIXTURE")
        with self._lock:self._latest=(meta,payload)
        self._state="ONLINE";self._reason="TEST FIXTURE ONLY — NOT HARDWARE"
    def read_frame(self,now_ns:int)->CameraFrame:
        with self._lock:latest=self._latest
        if not latest:return CameraFrame(CameraFrameMetadata("vehicle_rgb_camera","PI_UVC","NOT_CONNECTED" if self._state=="NOT_CONNECTED" else self._state,None,None,None,None,self._reason,camera_id="vehicle_rgb_camera",device_path=self.config.device_path or None,dropped_frames=self._dropped,backend=f"OpenCV/V4L2 reconnects={self._reconnects}"),None,None)
        meta,payload=latest;age=max(0.0,(now_ns-meta.timestamp_ns)/1e6);state="STALE" if age>self.config.stale_ms else meta.state;reason="CAMERA FRAME STALE" if state=="STALE" else meta.reason
        return CameraFrame(CameraFrameMetadata(**{**meta.__dict__,"state":state,"age_ms":age,"reason":reason}),None,payload)
    def health(self,now_ns:int)->DeviceHealth:
        frame=self.read_frame(now_ns);m=frame.metadata;return DeviceHealth("camera",m.source_mode,m.state,m.timestamp_ns,m.age_ms,None,m.reason)
    def stream_available(self,now_ns:int)->bool:return self.read_frame(now_ns).metadata.state=="ONLINE"
    def latest_jpeg(self,now_ns:int)->bytes|None:return self.read_frame(now_ns).payload
