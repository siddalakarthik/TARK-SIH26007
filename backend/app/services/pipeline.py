from __future__ import annotations
import time, uuid
from dataclasses import dataclass, field
from math import hypot
from app.config import Settings
from app.domain.models import *

def freshness(last_seen_ns:int|None, now_ns:int, fresh_ms:int, stale_ms:int)->Freshness:
    if last_seen_ns is None:return Freshness.MISSING
    age=(now_ns-last_seen_ns)/1e6
    return Freshness.FRESH if age<=fresh_ms else Freshness.AGING if age<=stale_ms else Freshness.STALE

def ttc(track:RadarTrack|None, now_ns:int, stale_ms:int)->TTCResult:
    if track is None:return TTCResult(status=TTCStatus.INVALID,seconds=None,reason="MISSING_TRACK")
    if (now_ns-track.last_update_ns)/1e6>stale_ms:return TTCResult(status=TTCStatus.INVALID,seconds=None,reason="STALE_TRACK")
    distance=hypot(track.x_m,track.y_m); closing=-track.relative_velocity_mps
    if closing<=1e-6:return TTCResult(status=TTCStatus.NOT_APPLICABLE,seconds=None,reason="NON_CLOSING")
    if distance<=0:return TTCResult(status=TTCStatus.INVALID,seconds=None,reason="NON_POSITIVE_RANGE")
    return TTCResult(status=TTCStatus.VALID,seconds=distance/closing,reason="CLOSING_TRACK")

def stopping(speed_mps:float, settings:Settings)->StoppingRequirement:
    r=settings.reaction_bound_s.value; a=settings.effective_deceleration_mps2.value; m=settings.margin_m.value
    return StoppingRequirement(reaction_distance_m=speed_mps*r,braking_distance_m=(speed_mps**2)/(2*a),margin_m=m,total_m=speed_mps*r+(speed_mps**2)/(2*a)+m,status="PARAMETERIZED / NOT VALIDATED")

def pvsoe(track:RadarTrack|None, health:SensorHealth, current_speed_mps:float, settings:Settings, now_ns:int)->PVSOEResult:
    stop=stopping(current_speed_mps,settings); d_env=0.0 if track is None else max(0.0,hypot(track.x_m,track.y_m)-track.uncertainty_m)
    constraints=[]; state=SafetyState.NORMAL; reason=ReasonCode.NORMAL_EVIDENCE
    if health.freshness in {Freshness.MISSING,Freshness.STALE}:
        state=SafetyState.UNKNOWN; reason=ReasonCode.UNKNOWN_STALE; constraints.append("sensor_not_fresh")
    elif d_env<=0:
        state=SafetyState.STOP; reason=ReasonCode.STOP_NO_ENVELOPE; constraints.append("no_usable_envelope")
    elif stop.total_m>d_env:
        state=SafetyState.RESTRICT; reason=ReasonCode.RESTRICT_ENVELOPE; constraints.append("stopping_requirement_exceeds_envelope")
    permitted=0.0  # Phase 1 hard cap: bounded command representation only; traction disabled.
    return PVSOEResult(D_env_m=d_env,D_base_m=d_env,D_effective_m=d_env,T_bound_s=settings.reaction_bound_s.value,stopping_requirement_m=stop.total_m,permitted_speed_mps=permitted,hard_cap_mps=settings.hard_cap_mps,active_constraints=constraints,state=state,reason_code=reason)

@dataclass
class Pipeline:
    settings:Settings; tracks:dict[str,RadarTrack]=field(default_factory=dict); events:list[SystemEvent]=field(default_factory=list); last_seen_ns:int|None=None; sequence:int=0
    def ingest(self,detections:list[RadarDetection],now_ns:int|None=None)->PVSOEResult:
        now_ns=now_ns or time.monotonic_ns(); self.last_seen_ns=now_ns
        for d in detections:
            key=f"ld2450:{d.candidate_id}"; existing=self.tracks.get(key)
            state=TrackState.TRACKED if existing else TrackState.NEW
            self.tracks[key]=RadarTrack(track_id=key,state=state,x_m=d.x_m,y_m=d.y_m,relative_velocity_mps=d.velocity_mps,quality=d.quality,uncertainty_m=d.uncertainty_m,first_seen_ns=existing.first_seen_ns if existing else now_ns,last_update_ns=now_ns)
        return self.decision(now_ns)
    def health(self,now_ns:int)->SensorHealth:
        f=freshness(self.last_seen_ns,now_ns,self.settings.fresh_age_ms,self.settings.stale_age_ms)
        state={Freshness.FRESH:HealthState.ONLINE,Freshness.AGING:HealthState.DEGRADED,Freshness.STALE:HealthState.STALE,Freshness.MISSING:HealthState.NOT_CONNECTED}[f]
        age=None if self.last_seen_ns is None else (now_ns-self.last_seen_ns)/1e6
        return SensorHealth(sensor_id="ld2450",state=state,freshness=f,last_seen_ns=self.last_seen_ns,age_ms=age,quality=None,reason=f"freshness_{f}")
    def decision(self,now_ns:int)->PVSOEResult:
        active=[t for t in self.tracks.values() if (now_ns-t.last_update_ns)/1e6<=self.settings.track_timeout_ms]
        track=min(active,key=lambda x:hypot(x.x_m,x.y_m)) if active else None
        result=pvsoe(track,self.health(now_ns),0.0,self.settings,now_ns)
        self.events.append(SystemEvent(event_id=str(uuid.uuid4()),timestamp_ns=now_ns,event_type="PVSOE_DECISION",severity="INFO",reason=result.reason_code.value,payload=result.model_dump(mode="json")))
        self.events=self.events[-1000:]
        return result
    def command(self,result:PVSOEResult,now_ns:int)->BoundedCommand:
        self.sequence+=1
        return BoundedCommand(sequence=self.sequence,timestamp_ns=now_ns,valid_until_ns=now_ns+self.settings.esp32_timeout_ms*1_000_000,state=result.state,permitted_speed_mps=result.permitted_speed_mps,left_command=0.0,right_command=0.0,heartbeat=self.sequence,reason_code=result.reason_code,configuration_hash=self.settings.configuration_hash)

