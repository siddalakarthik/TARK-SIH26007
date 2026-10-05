"""Versioned, explicit time/calibration/configuration evidence; no default transforms."""
from __future__ import annotations
from copy import deepcopy
from typing import Literal
from pydantic import Field, model_validator
from app.r3.contracts import Contract, Count, Finite, Nonnegative, Token, Observation, digest


class ClockMapping(Contract):
    mapping_id: Token
    source_id: Token
    clock_domain: Token
    source_boot_id: Token
    host_epoch: Token
    native_anchor: Count
    host_anchor_ns: Count
    ns_per_tick: Nonnegative
    offset_uncertainty_ns: Count
    drift_ppm: Finite
    drift_uncertainty_ppm: Nonnegative
    last_synchronization_ns: Count
    valid_until_ns: Count
    max_drift_ppm: Nonnegative
    evidence_reference: Token
    status: Literal['TIME_VALID','TIME_DEGRADED','TIME_UNSYNCED','CLOCK_RESET']
    @model_validator(mode='after')
    def bounded_mapping(self):
        if self.ns_per_tick<=0 or self.valid_until_ns<=self.last_synchronization_ns:
            raise ValueError('invalid mapping scale or lifetime')
        return self


class ClockRegistry:
    def __init__(self): self.records:dict[str,ClockMapping]={}
    def register(self, mapping:ClockMapping):
        existing=self.records.get(mapping.mapping_id)
        if existing and existing!=mapping: raise ValueError('clock mapping IDs are immutable')
        if len(self.records)>=256 and not existing: raise ValueError('clock registry full')
        self.records[mapping.mapping_id]=mapping.model_copy(deep=True)
    def capture(self, mapping_id:str, native:int, *, source_id:str, boot_id:str, host_epoch:str, now:int):
        m=self.records.get(mapping_id)
        if m is None: return None,None,'TIME_UNSYNCED'
        if (m.source_id,m.source_boot_id,m.host_epoch)!=(source_id,boot_id,host_epoch): return None,None,'CLOCK_RESET'
        if type(native) is not int or native<m.native_anchor or now<m.last_synchronization_ns: return None,None,'TIMESTAMP_INVALID'
        if now>m.valid_until_ns: return None,None,'TIME_UNSYNCED'
        if abs(m.drift_ppm)>m.max_drift_ppm: return None,None,'CLOCK_DRIFT_EXCEEDED'
        if m.status!='TIME_VALID': return None,None,m.status
        capture=round(m.host_anchor_ns+(native-m.native_anchor)*m.ns_per_tick*(1+m.drift_ppm/1_000_000))
        uncertainty=m.offset_uncertainty_ns+int((now-m.last_synchronization_ns)*m.drift_uncertainty_ppm/1_000_000+0.999999)
        if capture<0 or capture>now: return None,None,'TIMESTAMP_INVALID'
        return capture,uncertainty,'TIME_VALID'
    def snapshot(self): return [x.model_dump(mode='json') for x in self.records.values()]


CALIBRATION_KINDS={'RADAR_TO_BODY','RGB_TO_BODY','THERMAL_TO_BODY','IMU_TO_BODY','GNSS_A_TO_BODY','GNSS_B_TO_BODY','ENCODER_GEOMETRY','RGB_INTRINSICS','THERMAL_ALIGNMENT'}


class Calibration(Contract):
    calibration_id: Token
    version: Token
    kind: Token
    asset_ids: list[Token] = Field(min_length=1,max_length=8)
    mount_revision: Token
    method: Token
    date: Token
    operator: Token
    transform: list[Finite] | None = Field(default=None,max_length=16)
    parameters: dict[str,Finite] = Field(default_factory=dict)
    units: Token
    coordinate_frame_convention: Token
    residuals: dict[str,Nonnegative]
    validity_domain: Token
    software_version: Token
    artifacts: list[Token] = Field(min_length=1,max_length=16)
    @model_validator(mode='after')
    def checked_geometry(self):
        if self.kind not in CALIBRATION_KINDS: raise ValueError('unapproved calibration kind')
        if self.kind.endswith('_TO_BODY'):
            t=self.transform
            if t is None or len(t)!=16 or t[12:]!=[0,0,0,1]: raise ValueError('homogeneous transform required')
            rows=[t[i:i+3] for i in (0,4,8)]
            for i in range(3):
                for j in range(3):
                    if abs(sum(a*b for a,b in zip(rows[i],rows[j]))-(1 if i==j else 0))>1e-5: raise ValueError('rotation not orthonormal')
            a,b,c=rows
            det=a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
            if abs(det-1)>1e-5: raise ValueError('reflection is not a rotation')
        elif not self.parameters: raise ValueError('calibration parameters required')
        if not self.residuals: raise ValueError('calibration residuals required')
        return self


class CalibrationRegistry:
    def __init__(self): self.records:dict[str,Calibration]={}; self.invalid:dict[str,str]={}
    def register(self, record:Calibration):
        key=f'{record.calibration_id}:{record.version}'
        if key in self.records and self.records[key]!=record: raise ValueError('calibration version immutable')
        if len(self.records)>=256 and key not in self.records: raise ValueError('calibration registry full')
        self.records[key]=record.model_copy(deep=True)
    def invalidate(self,key:str,reason:str):
        if key not in self.records: raise ValueError('unknown calibration')
        if not reason: raise ValueError('invalidation reason required')
        self.invalid[key]=reason[:128]
    def valid(self,key:str,*,kind:str,asset_id:str|None,mount_revision:str|None):
        record=self.records.get(key)
        return bool(record and key not in self.invalid and record.kind==kind and asset_id in record.asset_ids and record.mount_revision==mount_revision)
    def snapshot(self): return {'records':[r.model_dump(mode='json') for r in self.records.values()],'invalid':deepcopy(self.invalid)}


class ConfigurationBundle(Contract):
    bundle_id: Token
    hardware_profile: Token
    driver_profile: Token
    sensor_modes: dict[str,Token]
    radar_profile: Token | None
    camera_mode: Token | None
    thermal_mode: Token | None
    gnss_configuration: Token | None
    network_profile: Token
    calibration_bundle: dict[str,list[Token]]
    mounts: dict[str,Token]
    ai_model: Token | None
    pvsoe_parameter_set: Token
    vehicle_parameters: dict[str,Finite | None]
    software_version: Token
    @property
    def content_hash(self): return digest(self.model_dump(mode='json'))


class ConfigurationRegistry:
    def __init__(self): self.records:dict[str,ConfigurationBundle]={}
    def register(self,bundle:ConfigurationBundle):
        if bundle.bundle_id in self.records and self.records[bundle.bundle_id]!=bundle: raise ValueError('configuration ID immutable')
        if len(self.records)>=64 and bundle.bundle_id not in self.records: raise ValueError('configuration registry full')
        self.records[bundle.bundle_id]=bundle.model_copy(deep=True)
    def require(self,observation:Observation)->ConfigurationBundle:
        bundle=self.records.get(observation.provenance.configuration_bundle_id)
        if bundle is None or observation.measurement.configuration_hash!=bundle.content_hash: raise ValueError('configuration bundle mismatch')
        if observation.provenance.software_version!=bundle.software_version: raise ValueError('software version mismatch')
        return bundle
