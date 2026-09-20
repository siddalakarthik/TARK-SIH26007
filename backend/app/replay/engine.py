from __future__ import annotations
from dataclasses import dataclass
from pydantic import ValidationError
from app.config import Settings
from app.domain.models import RadarDetection
from app.sensors.ld2450.parser import LD2450Parser
from app.services.pipeline import Pipeline

@dataclass
class ReplayResult: result:str; first_divergence:int|None; decisions:list[dict]
def replay(lines:list[bytes], pipeline:Pipeline, timestamps_ns:list[int])->ReplayResult:
    parser=LD2450Parser(); decisions=[]
    for i,(line,ts) in enumerate(zip(lines,timestamps_ns)):
        decisions.append(pipeline.ingest(parser.parse(line,ts),ts).model_dump(mode="json"))
    return ReplayResult(result="MATCH",first_divergence=None,decisions=decisions)
def compare(original:list[dict], replayed:list[dict])->ReplayResult:
    for i,(a,b) in enumerate(zip(original,replayed)):
        if a!=b:return ReplayResult("MISMATCH",i,replayed)
    return ReplayResult("MATCH" if len(original)==len(replayed) else "MISMATCH",None if len(original)==len(replayed) else min(len(original),len(replayed)),replayed)

class ReplayFormatError(ValueError): pass
class ReplayConfigurationError(ReplayFormatError): pass

def replay_timeline(records:list[dict], session:dict, configuration_hash:str)->dict:
    """Build a bounded, observation-only timeline from persisted evidence.

    Raw vendor frames deliberately remain non-replayable until the LD2450
    protocol is reviewed.  The returned source is always REPLAY, never LIVE.
    """
    if session.get("configuration_hash") != configuration_hash:
        raise ReplayConfigurationError("recording configuration hash is incompatible with active configuration")
    items=[]; previous_sequence=0; previous_timestamp=None
    for record in records:
        if record.get("kind") != "OBSERVATION_TICK_V1":
            continue
        sequence=record.get("sequence"); timestamp_ns=record.get("timestamp_ns"); payload=record.get("payload")
        if not isinstance(sequence,int) or sequence<=previous_sequence:
            raise ReplayFormatError("recording sequence is invalid")
        if not isinstance(timestamp_ns,int) or timestamp_ns<0 or (previous_timestamp is not None and timestamp_ns<previous_timestamp):
            raise ReplayFormatError("recording timeline is out of order")
        if not isinstance(payload,dict) or payload.get("schema_version")!=1:
            raise ReplayFormatError("unsupported recording payload")
        raw_detections=payload.get("radar_detections")
        decision=payload.get("decision"); event=payload.get("event"); command=payload.get("command")
        if not isinstance(raw_detections,list) or not isinstance(decision,dict) or not isinstance(event,dict) or not isinstance(command,dict):
            raise ReplayFormatError("recording misses normalized replay evidence")
        try:
            detections=[RadarDetection.model_validate(item) for item in raw_detections]
        except (ValidationError,TypeError) as error:
            raise ReplayFormatError("invalid normalized radar detection") from error
        items.append({
            "position":len(items),"sequence":sequence,"timestamp_ns":timestamp_ns,
            "source_mode":"REPLAY","original_source_mode":record.get("source_mode"),
            "decision":decision,"event":event,"command":command,"track_count":len(detections),
        })
        previous_sequence=sequence; previous_timestamp=timestamp_ns
    if not items:
        return {"session_id":session.get("session_id"),"source_mode":"REPLAY","state":"NO_REPLAYABLE_OBSERVATIONS","items":[],"start_timestamp_ns":None,"end_timestamp_ns":None,"duration_ns":0,"configuration_hash":configuration_hash}
    return {"session_id":session.get("session_id"),"source_mode":"REPLAY","state":"READY","items":items,"start_timestamp_ns":items[0]["timestamp_ns"],"end_timestamp_ns":items[-1]["timestamp_ns"],"duration_ns":items[-1]["timestamp_ns"]-items[0]["timestamp_ns"],"configuration_hash":configuration_hash}

def replay_recording(records:list[dict], settings:Settings)->ReplayResult:
    """Deterministically recompute a persisted observation-only session.

    Raw vendor frames are retained for diagnostics but are not decoded here
    without an authoritative protocol definition.  Only the normalized tick
    format written by RecordingStore is replayable.
    """
    pipeline=Pipeline(settings); expected=[]; replayed=[]
    for record in records:
        if record.get("kind")!="OBSERVATION_TICK_V1": continue
        payload=record.get("payload")
        if not isinstance(payload,dict) or payload.get("schema_version")!=1:
            raise ReplayFormatError("unsupported recording payload")
        raw_detections=payload.get("radar_detections")
        if not isinstance(raw_detections,list): raise ReplayFormatError("recording misses radar_detections")
        try: detections=[RadarDetection.model_validate(item) for item in raw_detections]
        except (ValidationError,TypeError) as error: raise ReplayFormatError("invalid normalized radar detection") from error
        timestamp_ns=record.get("timestamp_ns")
        if not isinstance(timestamp_ns,int) or timestamp_ns<0: raise ReplayFormatError("invalid recording timestamp")
        decision=pipeline.ingest(detections,timestamp_ns) if detections else pipeline.decision(timestamp_ns)
        replayed.append(decision.model_dump(mode="json"))
        saved=payload.get("decision")
        if not isinstance(saved,dict): raise ReplayFormatError("recording misses decision evidence")
        expected.append(saved)
    if not replayed: raise ReplayFormatError("recording has no replayable observation ticks")
    return compare(expected,replayed)
