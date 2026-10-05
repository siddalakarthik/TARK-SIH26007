"""Device-specific decoded boundaries. No automatic probing or legacy substitution.

Raw vendor parsing requires a named documented mode. These validators also accept
synthetic fixtures explicitly labelled SIMULATION; they do not assert wire support.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from typing import Callable, Protocol
from pydantic import Field, model_validator
from app.r3.contracts import Contract, Count, Finite, Nonnegative, Token


class RadarPoint(Contract):
    x_m: Finite
    y_m: Finite
    z_m: Finite
    radial_velocity_mps: Finite
    snr_db: Finite | None = None

class TiRadarFrame(Contract):
    firmware_profile: Token
    frame_number: Count
    cpu_cycles: Count | None = None
    points: list[RadarPoint] = Field(max_length=256)
    # TI firmware sensor axes are retained; no implicit body-frame transform.
    sensor_frame: Token = 'TI_PROFILE_AXES_UNQUALIFIED'

class ImageSemantic(Contract):
    label: Token
    box_xyxy_pixels: list[Nonnegative] = Field(min_length=4,max_length=4)
    confidence: float = Field(ge=0,le=1)
    @model_validator(mode='after')
    def valid_box(self):
        x1,y1,x2,y2=self.box_xyxy_pixels
        if x1>=x2 or y1>=y2:raise ValueError('invalid image box')
        return self

class UvcFrame(Contract):
    frame_id: Token
    width: int = Field(gt=0,le=4096)
    height: int = Field(gt=0,le=2160)
    pixel_format: Token
    media_reference: Token
    sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    pts: Count | None = None
    exposure_us: Nonnegative | None = None
    timestamp_semantics: Token = 'UNKNOWN'
    detections: list[ImageSemantic] = Field(default_factory=list,max_length=64)
    inference_qualification: str = Field(pattern=r'^(UNVALIDATED|CONFIGURED_RESEARCH)$',default='UNVALIDATED')
    model_reference: Token | None = None
    @model_validator(mode='after')
    def semantic_metadata(self):
        if self.detections and self.model_reference is None:raise ValueError('image semantics require model provenance')
        if any(d.box_xyxy_pixels[2]>self.width or d.box_xyxy_pixels[3]>self.height for d in self.detections):raise ValueError('box outside image')
        return self

class LeptonFrame(UvcFrame):
    ffc_state: str = Field(pattern=r'^(UNKNOWN|ACTIVE|IDLE)$')
    radiometry: str = Field(pattern=r'^(UNAVAILABLE|VERIFIED_TLINEAR)$')
    temperatures_c: list[Finite] | None = Field(default=None,max_length=19200)
    @model_validator(mode='after')
    def exact_thermal_mode(self):
        if self.width!=160 or self.height!=120: raise ValueError('Lepton 3.5 image must be 160x120; strip documented telemetry rows in driver')
        if self.temperatures_c is not None and (self.radiometry!='VERIFIED_TLINEAR' or len(self.temperatures_c)!=19200):
            raise ValueError('no invented temperature conversion')
        return self

class Bno085Sample(Contract):
    report_id: Count
    quaternion_xyzw: list[Finite] | None = Field(default=None,min_length=4,max_length=4)
    angular_velocity_rad_s: list[Finite] | None = Field(default=None,min_length=3,max_length=3)
    acceleration_m_s2: list[Finite] | None = Field(default=None,min_length=3,max_length=3)
    sh2_timestamp_us: Count | None = None
    accuracy_status: int | None = Field(default=None,ge=0,le=3)
    @model_validator(mode='after')
    def usable_report(self):
        if all(v is None for v in (self.quaternion_xyzw,self.angular_velocity_rad_s,self.acceleration_m_s2)): raise ValueError('empty IMU report')
        if self.quaternion_xyzw and abs(sum(v*v for v in self.quaternion_xyzw)-1)>0.05: raise ValueError('invalid orientation quaternion')
        return self

class Lg290pFix(Contract):
    fix_type: str = Field(pattern=r'^(NO_FIX|STANDALONE|DGPS|RTK_FLOAT|RTK_FIXED|UNKNOWN)$')
    latitude_deg: Finite | None = Field(default=None,ge=-90,le=90)
    longitude_deg: Finite | None = Field(default=None,ge=-180,le=180)
    altitude_m: Finite | None = None
    satellites: Count | None = None
    speed_mps: Nonnegative | None = None
    course_deg: Nonnegative | None = Field(default=None,lt=360)
    horizontal_uncertainty_m: Nonnegative | None = None
    correction_age_s: Nonnegative | None = None
    receiver_utc: Token | None = None
    datum: Token = 'WGS84'
    @model_validator(mode='after')
    def no_fake_fix(self):
        if (self.latitude_deg is None)!=(self.longitude_deg is None): raise ValueError('coordinate pair incomplete')
        if self.fix_type in {'NO_FIX','UNKNOWN'} and self.latitude_deg is not None: raise ValueError('no-fix cannot supply valid location')
        if self.fix_type not in {'NO_FIX','UNKNOWN'} and self.latitude_deg is None: raise ValueError('valid fix requires coordinates')
        if self.course_deg is not None and (self.speed_mps is None or self.speed_mps==0): raise ValueError('stationary GNSS course unavailable; never body heading')
        return self

class EncoderSample(Contract):
    left_count: int = Field(ge=-(2**31),le=2**31-1)
    right_count: int = Field(ge=-(2**31),le=2**31-1)
    interval_start_ns: Count
    interval_end_ns: Count
    invalid_edges: Count
    lost_edges: Count | None = None
    @model_validator(mode='after')
    def interval(self):
        if self.interval_end_ns<=self.interval_start_ns: raise ValueError('encoder interval must be positive')
        return self


DECODERS={'ti_iwr6843':TiRadarFrame,'uvc_rgb':UvcFrame,'lepton_purethermal':LeptonFrame,
          'bno085':Bno085Sample,'lg290p':Lg290pFix,'node_b':Lg290pFix,'esp32_encoder':EncoderSample}

def validate_sample(adapter:str,payload:dict)->dict:
    if adapter not in DECODERS: raise ValueError('unsupported R3 adapter; legacy is separate')
    return DECODERS[adapter].model_validate(payload).model_dump(mode='json')

class Reader(Protocol):
    def read(self)->dict|None: ...
    def close(self)->None: ...

@dataclass
class ConfiguredReader:
    """Single bounded pump; real drivers injected only by approved integration code.

    Opening is deliberately outside this object. A config flag alone must never
    import a serial/USB/I2C SDK or select the first available physical device.
    """
    adapter: str
    factory: Callable[[],Reader]
    on_sample: Callable[[dict],None]
    reconnect_ns: int = 1_000_000_000
    reader: Reader|None = None
    next_retry_ns: int = 0
    state: str = 'NOT_CONNECTED'
    error: str|None = None
    closed: bool = False
    def pump(self,now_ns:int):
        if self.closed or now_ns<self.next_retry_ns: return
        try:
            if self.reader is None: self.reader=self.factory(); self.state='DRIVER_READY'
            sample=self.reader.read()
            if sample is not None:
                self.on_sample(validate_sample(self.adapter,sample)); self.state='PRODUCING'; self.error=None
        except Exception as error:
            self.error=type(error).__name__; self.state='UNAVAILABLE'; self.next_retry_ns=now_ns+self.reconnect_ns
            if self.reader is not None:
                try: self.reader.close()
                except Exception: pass
            self.reader=None
    def close(self):
        self.closed=True
        try:
            if self.reader: self.reader.close()
        finally: self.reader=None; self.state='NOT_CONNECTED'
