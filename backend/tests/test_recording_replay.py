from pathlib import Path

import pytest

from app.config import Settings
from app.domain.models import RadarDetection
from app.replay.engine import ReplayConfigurationError, ReplayFormatError, replay_recording, replay_timeline
from app.replay.store import RecordingError, RecordingStore
from app.services.pipeline import Pipeline


SETTINGS = Settings.from_file(Path(__file__).parents[2] / "config" / "phase1.json")


def recording_payload(timestamp_ns: int = 1_000_000_000) -> dict:
    detection = RadarDetection(candidate_id=7, x_m=3.0, y_m=0.0, velocity_mps=-1.0, quality=0.9, uncertainty_m=0.2, timestamp_ns=timestamp_ns)
    decision = Pipeline(SETTINGS).ingest([detection], timestamp_ns)
    return {"schema_version": 1, "radar_detections": [detection.model_dump(mode="json")], "decision": decision.model_dump(mode="json"), "event":{"event_id":"fixture","timestamp_ns":timestamp_ns,"event_type":"PVSOE_DECISION","severity":"INFO","reason":"FIXTURE"}, "command":Pipeline(SETTINGS).command(decision,timestamp_ns).model_dump(mode="json")}


def test_recording_catalog_selection_and_deterministic_replay(tmp_path):
    store = RecordingStore(tmp_path / "recordings.db")
    assert store.list() == []
    session = store.start(timestamp_ns=1, source_mode="SIMULATION", configuration_hash=SETTINGS.configuration_hash, max_records=2)
    assert session["status"] == "RECORDING"
    assert store.append_observation_tick(timestamp_ns=1_000_000_000, source_mode="SIMULATION", payload=recording_payload())
    completed = store.stop(timestamp_ns=2_000_000_000)
    assert completed["status"] == "COMPLETE" and completed["record_count"] == 1
    assert store.list()[0]["session_id"] == completed["session_id"]
    records = store.records(completed["session_id"])
    assert [record["sequence"] for record in records] == [1]
    assert replay_recording(records, SETTINGS).result == "MATCH"
    with pytest.raises(RecordingError, match="not found"):
        store.get("missing")
    store.close()


def test_recording_is_bounded_and_never_silently_overwrites(tmp_path):
    store = RecordingStore(tmp_path / "recordings.db")
    session = store.start(timestamp_ns=1, source_mode="SIMULATION", configuration_hash=SETTINGS.configuration_hash, max_records=1)
    assert store.append_observation_tick(timestamp_ns=2, source_mode="SIMULATION", payload=recording_payload())
    assert not store.append_observation_tick(timestamp_ns=3, source_mode="SIMULATION", payload=recording_payload())
    assert store.get(session["session_id"])["status"] == "FULL"
    assert store.get(session["session_id"])["record_count"] == 1
    store.close()


def test_corrupted_or_empty_recording_is_rejected_safely(tmp_path):
    store = RecordingStore(tmp_path / "recordings.db")
    session = store.start(timestamp_ns=1, source_mode="SIMULATION", configuration_hash=SETTINGS.configuration_hash, max_records=2)
    store.db.execute("INSERT INTO recording_records VALUES (?,?,?,?,?,?)", (session["session_id"], 1, 2, "SIMULATION", "OBSERVATION_TICK_V1", "not-json"))
    store.db.execute("UPDATE recording_sessions SET record_count=1 WHERE id=?", (session["session_id"],))
    store.db.commit()
    with pytest.raises(RecordingError, match="corrupted JSON"):
        store.records(session["session_id"])
    with pytest.raises(ReplayFormatError, match="no replayable"):
        replay_recording([], SETTINGS)
    store.close()


def test_replay_timeline_has_ordered_replay_source_bounds_and_config_gate(tmp_path):
    store=RecordingStore(tmp_path/"recordings.db")
    session=store.start(timestamp_ns=1,source_mode="SIMULATION",configuration_hash=SETTINGS.configuration_hash,max_records=3)
    assert store.append_observation_tick(timestamp_ns=1_000_000_000,source_mode="SIMULATION",payload=recording_payload(1_000_000_000))
    assert store.append_observation_tick(timestamp_ns=2_000_000_000,source_mode="SIMULATION",payload=recording_payload(2_000_000_000))
    session=store.stop(timestamp_ns=3_000_000_000);records=store.records(session["session_id"])
    timeline=replay_timeline(records,session,SETTINGS.configuration_hash)
    assert timeline["source_mode"]=="REPLAY" and timeline["state"]=="READY"
    assert [item["position"] for item in timeline["items"]]==[0,1]
    assert [item["timestamp_ns"] for item in timeline["items"]]==[1_000_000_000,2_000_000_000]
    assert timeline["duration_ns"]==1_000_000_000 and all(item["source_mode"]=="REPLAY" for item in timeline["items"])
    with pytest.raises(ReplayConfigurationError,match="incompatible"):
        replay_timeline(records,session,"other-config")
    store.close()
