from __future__ import annotations

from enum import StrEnum
from math import isfinite
from pydantic import BaseModel, Field, field_validator


class HealthState(StrEnum): ONLINE="ONLINE"; DEGRADED="DEGRADED"; STALE="STALE"; FAILED="FAILED"; UNKNOWN="UNKNOWN"; NOT_CONNECTED="NOT_CONNECTED"; NOT_YET_VERIFIED="NOT_YET_VERIFIED"
class Freshness(StrEnum): FRESH="FRESH"; AGING="AGING"; STALE="STALE"; MISSING="MISSING"
class TrackState(StrEnum): NEW="NEW"; TENTATIVE="TENTATIVE"; TRACKED="TRACKED"; LOST="LOST"; EXPIRED="EXPIRED"
class TTCStatus(StrEnum): VALID="TTC_VALID"; INVALID="TTC_INVALID"; NOT_APPLICABLE="TTC_NOT_APPLICABLE"
class SafetyState(StrEnum): NORMAL="NORMAL"; WARN="WARN"; RESTRICT="RESTRICT"; UNKNOWN="UNKNOWN"; STOP="STOP"
class ReasonCode(StrEnum): NORMAL_EVIDENCE="NORMAL_EVIDENCE"; WARN_MARGIN="WARN_MARGIN"; RESTRICT_ENVELOPE="RESTRICT_ENVELOPE"; RESTRICT_SENSOR="RESTRICT_SENSOR"; UNKNOWN_STALE="UNKNOWN_STALE"; UNKNOWN_CONFLICT="UNKNOWN_CONFLICT"; STOP_NO_ENVELOPE="STOP_NO_ENVELOPE"; STOP_ENCODER="STOP_ENCODER"; STOP_HEARTBEAT="STOP_HEARTBEAT"; ESTOP_ACTIVE="ESTOP_ACTIVE"

class RadarDetection(BaseModel):
    source_id: str = "ld2450"
    candidate_id: int
    x_m: float
    y_m: float
    velocity_mps: float
    quality: float = Field(ge=0, le=1)
    timestamp_ns: int
    uncertainty_m: float = Field(ge=0)
    @field_validator("x_m", "y_m", "velocity_mps", "uncertainty_m")
    @classmethod
    def finite(cls, value: float) -> float:
        if not isfinite(value): raise ValueError("numeric field must be finite")
        return value

class RadarTrack(BaseModel):
    track_id: str; state: TrackState; x_m: float; y_m: float; relative_velocity_mps: float
    quality: float; uncertainty_m: float; first_seen_ns: int; last_update_ns: int; source_id: str="ld2450"

class SensorHealth(BaseModel):
    sensor_id: str; state: HealthState; freshness: Freshness; last_seen_ns: int | None; age_ms: float | None; quality: float | None; reason: str

class TTCResult(BaseModel): status: TTCStatus; seconds: float | None; reason: str
class StoppingRequirement(BaseModel): reaction_distance_m: float; braking_distance_m: float; margin_m: float; total_m: float; status: str
class PVSOEResult(BaseModel): D_env_m: float; D_base_m: float; D_effective_m: float; T_bound_s: float; stopping_requirement_m: float; permitted_speed_mps: float; hard_cap_mps: float; active_constraints: list[str]; state: SafetyState; reason_code: ReasonCode
class BoundedCommand(BaseModel): protocol_version:int=1; sequence:int=Field(ge=0); timestamp_ns:int; valid_until_ns:int; state:SafetyState; permitted_speed_mps:float=Field(ge=0); left_command:float=0; right_command:float=0; heartbeat:int; reason_code:ReasonCode; configuration_hash:str; checksum:int|None=None
class CommandResult(BaseModel): accepted:bool; reason:str; sequence:int; applied_left:float=0; applied_right:float=0
class SystemEvent(BaseModel): event_id:str; timestamp_ns:int; event_type:str; severity:str; reason:str; payload:dict

