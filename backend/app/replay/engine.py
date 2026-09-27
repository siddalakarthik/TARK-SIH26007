"""Observation-only replay. No transport or device dependencies."""
from __future__ import annotations
import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from pydantic import ValidationError
from app.config import Settings
from app.domain.models import RadarDetection, RadarTrack, PVSOEResult, SensorHealth, BoundedCommand, SystemEvent
from app.sensors.ld2450.parser import LD2450Parser
from app.services.pipeline import Pipeline

FORMAT_VERSION = 2
SOFTWARE_ID = "TARK_PROMPT2_REPLAY_V2"
MAX_SESSION_RECORDS = 50_000

class ReplayFormatError(ValueError): pass
class ReplayConfigurationError(ReplayFormatError): pass

@dataclass
class ReplayResult:
    result: str
    first_divergence: int | None
    decisions: list[dict]
    verified_records: int = 0
    verified_decisions: int = 0
    first_sequence: int | None = None
    last_sequence: int | None = None

def replay(lines: list[bytes], pipeline: Pipeline, timestamps_ns: list[int]) -> ReplayResult:
    if len(lines) != len(timestamps_ns):
        raise ReplayFormatError("input/time lengths differ")
    parser = LD2450Parser()
    decisions = [pipeline.ingest(parser.parse(line, ts), ts).model_dump(mode="json") for line, ts in zip(lines, timestamps_ns)]
    return ReplayResult("NOT_COMPARED", None, decisions)

def compare(original: list[dict], replayed: list[dict]) -> ReplayResult:
    for i, (a, b) in enumerate(zip(original, replayed)):
        if a != b: return ReplayResult("MISMATCH", i, replayed)
    same = len(original) == len(replayed)
    return ReplayResult("MATCH" if same else "MISMATCH", None if same else min(len(original), len(replayed)), replayed)

def _digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def software_fingerprint() -> str:
    # Software identity, not release authentication. No Git subprocess needed.
    root = Path(__file__).parents[1]
    digest = hashlib.sha256()
    for relative in ("services/pipeline.py", "services/system.py", "domain/models.py", "config.py", "replay/engine.py"):
        digest.update(relative.encode())
        digest.update((root / relative).read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()

def recording_metadata(pipeline: Pipeline) -> dict:
    return {"format_version": FORMAT_VERSION, "software_id": SOFTWARE_ID,
            "software_fingerprint": software_fingerprint(), "configuration_identifier": pipeline.settings.configuration_hash,
            "configuration_fingerprint": _digest(pipeline.settings.model_dump(mode="json",exclude={"mode"})),
            "input_schema": "ORDERED_RADAR_REPORTS_V2", "source_mode": pipeline.settings.mode.upper(),
            "checkpoint": {"version": 1, "tracks": [t.model_dump(mode="json") for t in pipeline.tracks.values()],
                           "last_seen_ns": pipeline.last_seen_ns, "timestamp_fault": pipeline.timestamp_fault, "sequence": pipeline.sequence}}

def _uint(value, name: str) -> int:
    if type(value) is not int or not 0 <= value <= 0x7FFF_FFFF_FFFF_FFFF:
        raise ReplayFormatError(f"invalid {name}")
    return value

def compatible_pipeline(session: dict, settings: Settings) -> Pipeline:
    if session.get("status") not in {"COMPLETE", "FULL", "INTERRUPTED"}:
        raise ReplayFormatError("recording must be stopped before full-session replay")
    if session.get("configuration_hash") != settings.configuration_hash:
        raise ReplayConfigurationError("recording configuration identifier is incompatible")
    metadata = session.get("metadata")
    if not isinstance(metadata, dict):
        raise ReplayConfigurationError("LEGACY_NONDETERMINISTIC: missing versioned initial state")
    if metadata.get("format_version") != FORMAT_VERSION or metadata.get("input_schema") != "ORDERED_RADAR_REPORTS_V2":
        raise ReplayConfigurationError("INCOMPATIBLE recording format/input schema")
    if metadata.get("software_id") != SOFTWARE_ID or metadata.get("software_fingerprint") != software_fingerprint():
        raise ReplayConfigurationError("INCOMPATIBLE software identity")
    if metadata.get("configuration_identifier") != settings.configuration_hash or metadata.get("configuration_fingerprint") != _digest(settings.model_dump(mode="json",exclude={"mode"})):
        raise ReplayConfigurationError("INCOMPATIBLE configuration values")
    if metadata.get("source_mode") != session.get("source_mode") or metadata.get("source_mode") not in {"SIMULATION","REAL_RADAR","REPLAY"}:
        raise ReplayConfigurationError("INCOMPATIBLE source mode")
    if _uint(session.get("record_count"), "record count") > MAX_SESSION_RECORDS:
        raise ReplayFormatError("recording exceeds supported bound")
    checkpoint = metadata.get("checkpoint")
    if not isinstance(checkpoint, dict) or checkpoint.get("version") != 1 or not isinstance(checkpoint.get("tracks"), list):
        raise ReplayFormatError("missing or invalid initial checkpoint")
    if type(checkpoint.get("timestamp_fault")) is not bool:
        raise ReplayFormatError("invalid checkpoint timestamp_fault")
    pipeline = Pipeline(settings)
    pipeline.sequence = _uint(checkpoint.get("sequence"), "checkpoint sequence")
    pipeline.last_seen_ns = checkpoint.get("last_seen_ns")
    if pipeline.last_seen_ns is not None: _uint(pipeline.last_seen_ns, "checkpoint timestamp")
    pipeline.timestamp_fault = checkpoint["timestamp_fault"]
    try:
        for raw in checkpoint["tracks"]:
            track = RadarTrack.model_validate(raw)
            if track.track_id in pipeline.tracks: raise ReplayFormatError("duplicate checkpoint track")
            RadarDetection(candidate_id=0, x_m=track.x_m, y_m=track.y_m, velocity_mps=track.relative_velocity_mps,
                           quality=track.quality, uncertainty_m=track.uncertainty_m, timestamp_ns=track.last_update_ns)
            if _uint(track.first_seen_ns, "track first time") > track.last_update_ns:
                raise ReplayFormatError("invalid checkpoint track times")
            pipeline.tracks[track.track_id] = track
    except (ValidationError, TypeError) as error:
        raise ReplayFormatError("invalid checkpoint track") from error
    return pipeline

def _ticks(records: Iterable[dict], session: dict):
    count = 0
    last_tick_ns = None
    for record in records:
        count += 1
        if count > MAX_SESSION_RECORDS or _uint(record.get("sequence"), "record sequence") != count:
            raise ReplayFormatError("missing, duplicated or out-of-order record")
        timestamp = _uint(record.get("timestamp_ns"), "record timestamp")
        payload = record.get("payload")
        if not isinstance(payload, dict): raise ReplayFormatError("invalid record payload")
        if record.get("kind") == "RAW_FRAME_V1":
            try:
                if payload.get("encoding") != "base64" or payload.get("schema_version") != 1: raise ValueError("raw schema")
                base64.b64decode(payload["raw"], validate=True)
            except (ValueError, TypeError, KeyError) as error:
                raise ReplayFormatError("corrupt diagnostic raw record") from error
            yield record, None
            continue
        if record.get("kind") != "OBSERVATION_TICK_V2" or payload.get("schema_version") != 2:
            raise ReplayFormatError("unsupported/legacy observation record")
        if record.get("source_mode") != session["source_mode"]:
            raise ReplayFormatError("tick source differs from recording source")
        if last_tick_ns is not None and timestamp < last_tick_ns:
            raise ReplayFormatError("recording timeline is out of order")
        last_tick_ns = timestamp
        reports = payload.get("observations")
        if not isinstance(reports, list) or len(reports) > 16:
            raise ReplayFormatError("missing or oversized ordered observation batch")
        normalized = []
        for order, report in enumerate(reports):
            if not isinstance(report, dict) or report.get("kind") != "RADAR_REPORT" or report.get("order") != order:
                raise ReplayFormatError("invalid observation order/type")
            expected_source = "SIMULATION" if session["source_mode"] == "SIMULATION" else "REAL"
            if report.get("source_mode") != expected_source or not isinstance(report.get("detections"), list):
                raise ReplayFormatError("invalid observation source/data")
            # Future source timestamps must reach the same live rejection path.
            observed_at = _uint(report.get("timestamp_ns"), "observation timestamp")
            try: detections = [RadarDetection.model_validate(item) for item in report["detections"]]
            except (ValidationError, TypeError) as error: raise ReplayFormatError("invalid normalized detection") from error
            normalized.append((observed_at, detections))
        for key in ("decision", "radar_health", "event", "command"):
            if not isinstance(payload.get(key), dict): raise ReplayFormatError(f"missing {key} evidence")
        try:
            json.dumps(payload, allow_nan=False)
            for key, model in (("decision", PVSOEResult), ("radar_health", SensorHealth), ("command", BoundedCommand), ("event", SystemEvent)):
                model.model_validate(payload[key])
        except (ValueError, TypeError) as error:
            raise ReplayFormatError("invalid saved decision/health/command/event evidence") from error
        yield record, normalized
    if count != session["record_count"]:
        raise ReplayFormatError("incomplete recording: catalog count differs from verified records")

def _event_semantics(event: dict) -> dict:
    return {key: value for key, value in event.items() if key != "event_id"}

def replay_recording(records: Iterable[dict], settings: Settings, session: dict | None = None) -> ReplayResult:
    if session is None:
        raise ReplayConfigurationError("LEGACY_NONDETERMINISTIC: session identity/checkpoint required")
    pipeline = compatible_pipeline(session, settings)
    result = ReplayResult("MATCH", None, [])
    for record, reports in _ticks(records, session):
        result.verified_records += 1
        result.first_sequence = result.first_sequence or record["sequence"]
        result.last_sequence = record["sequence"]
        if reports is None: continue
        now = record["timestamp_ns"]
        for observed_at, detections in reports: pipeline.observe(detections, observed_at, now)
        decision = pipeline.decision(now)
        command = pipeline.command(decision, now).model_dump(mode="json")
        actual = {"decision": decision.model_dump(mode="json"), "radar_health": pipeline.health(now).model_dump(mode="json"),
                  "command": command, "event": _event_semantics(pipeline.events[-1].model_dump(mode="json"))}
        saved = record["payload"]
        expected = {key: saved[key] for key in ("decision", "radar_health", "command")}
        expected["event"] = _event_semantics(saved["event"])
        if actual != expected and result.first_divergence is None:
            result.result = "MISMATCH"
            result.first_divergence = result.verified_decisions
        result.verified_decisions += 1
        # Entire session checked; only a bounded diagnostic preview returned.
        if len(result.decisions) < 100: result.decisions.append(actual["decision"])
    if not result.verified_decisions: raise ReplayFormatError("recording has no replayable observation ticks")
    return result

def replay_timeline(records: Iterable[dict], session: dict, settings: Settings) -> dict:
    compatible_pipeline(session, settings)
    items = []
    for record, reports in _ticks(records, session):
        if reports is None: continue
        payload = record["payload"]
        items.append({"position": len(items), "sequence": record["sequence"], "timestamp_ns": record["timestamp_ns"],
                      "source_mode": "REPLAY", "original_source_mode": record["source_mode"],
                      "decision": payload["decision"], "event": payload["event"], "command": payload["command"],
                      "track_count": sum(len(detections) for _, detections in reports)})
    start = items[0]["timestamp_ns"] if items else None
    end = items[-1]["timestamp_ns"] if items else None
    return {"session_id": session["session_id"], "source_mode": "REPLAY", "state": "READY" if items else "NO_REPLAYABLE_OBSERVATIONS",
            "items": items, "start_timestamp_ns": start, "end_timestamp_ns": end, "duration_ns": end-start if items else 0,
            "configuration_hash": settings.configuration_hash, "complete": True, "total_records": session["record_count"]}
