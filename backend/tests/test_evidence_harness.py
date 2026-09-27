"""Prompt-3 regressions: production paths, deterministic artifacts, fail-closed controls."""
from copy import deepcopy
import inspect
import json
from pathlib import Path
import shutil

import pytest
from pydantic import ValidationError
from app.evidence.artifacts import build_bundle, inventory, read_json, verify_bundle, write_json, NEGATIVES
from app.evidence.catalog import catalog
from app.evidence.controls import negative_controls
from app.evidence.runner import (ControlledRun, EvidenceFailure, ROOT, assert_zero,
                                 isolated_environment, run_scenario, settings)
from app.evidence.schema import Scenario, trace_digest


@pytest.fixture
def isolated(monkeypatch):
    for key in tuple(__import__("os").environ):
        if key.startswith("TARK_"): monkeypatch.delenv(key)
    monkeypatch.setenv("TARK_DATABASE_PATH", ":memory:")


@pytest.mark.parametrize("scenario", catalog(), ids=lambda x: x.scenario_id)
def test_all_production_scenarios(scenario, isolated):
    a, b = run_scenario(scenario, "first"), run_scenario(scenario, "second")
    assert a["result"] == b["result"] == "PASS"
    assert a["digest"] == b["digest"]
    assert a["replay"]["result"]["result"] == "MATCH"
    assert a["hardware_opener_calls"] == 0 and a["shutdown_complete"]


def test_observers_compare_entire_logical_trace(isolated):
    results = [run_scenario(s) for s in catalog()[15:18]]
    assert len({r["digest"] for r in results}) == 1
    assert not results[0]["trace"][0]["observer_reads"]["reads"]
    assert results[1]["trace"][0]["observer_reads"]["reads"]
    reads = results[2]["trace"][0]["observer_reads"]["reads"]
    assert len([r for r in reads if "websocket_cycle" in r]) == 6


@pytest.fixture(scope="module")
def reference():
    return run_scenario(catalog()[0])


@pytest.fixture(scope="module")
def controls(reference):
    return negative_controls(reference)


@pytest.mark.parametrize("name", sorted(NEGATIVES))
def test_negative_controls(name, controls):
    assert controls[name]["result"] == "PASS"


@pytest.mark.parametrize("mutation", ["unknown_field", "unknown_action", "wrong_type", "negative_time", "nan", "unknown_fact", "wrong_fact_type", "replay_before_stop", "double_start", "no_replay"])
def test_strict_scenario_validation(mutation):
    value = catalog()[0].model_dump()
    if mutation == "unknown_field": value["arbitrary_code"] = "eval"
    elif mutation == "unknown_action": value["steps"][0]["action"] = "MOVE_MOTOR"
    elif mutation == "wrong_type": value["steps"][0]["args"]["pi_ns"] = "100"
    elif mutation == "negative_time": value["steps"][0]["args"]["pi_ns"] = -1
    elif mutation == "nan": value["initial_reports"][0]["distance_m"] = float("nan")
    elif mutation == "unknown_fact": value["steps"][0]["expect"]["anything"] = 1
    elif mutation == "wrong_fact_type": value["steps"][0]["expect"]["sequence"] = True
    elif mutation == "replay_before_stop": value["steps"][0] = {"action": "VERIFY_REPLAY", "expect": {"replay": "MATCH"}}
    elif mutation == "double_start": value["steps"][0] = {"action": "START_RECORDING", "expect": {"sequence": 1}}
    elif mutation == "no_replay": value["steps"].pop()
    with pytest.raises(ValidationError): Scenario.model_validate(value)


@pytest.mark.parametrize("variable", ["TARK_MODE", "TARK_GNSS_DEVICE_PATH", "TARK_DATABASE_PATH", "TARK_ACCESS_TOKEN"])
def test_nonisolated_environment_rejected(variable, monkeypatch, isolated):
    monkeypatch.setenv(variable, "UNSAFE_FIXTURE_VALUE")
    with pytest.raises(EvidenceFailure, match="non-isolated"):
        with isolated_environment(): pytest.fail("guard allowed a configured runtime")


def test_tripwire_blocks_physical_start(isolated):
    from app.gnss_driver import GnssReader
    with pytest.raises(EvidenceFailure, match="TRIPWIRE"):
        with isolated_environment():
            GnssReader.start(None)


def test_production_entry_points_not_replaced(isolated):
    from app.main import create_app, DeploymentConfig
    from app.services.pipeline import Pipeline
    from app.services.runtime import RuntimeOwner
    from app.services.system import TarkSystem
    from app.communication.esp32.protocol import ESP32Client, ESP32ProtocolSimulator
    from app.evidence.runner import DeliveryEndpoint
    run = ControlledRun(catalog()[0], "identity-check")
    with isolated_environment():
        app = create_app(settings(), DeploymentConfig(), runtime_factory=run.factory)
        try:
            assert type(run.system) is TarkSystem
            assert type(run.system.pipeline) is Pipeline
            assert type(run.owner) is RuntimeOwner
            assert type(run.system.esp32_client) is ESP32Client
            assert run.submit_probe._mock_wraps.__func__ is ESP32Client.submit
            assert DeliveryEndpoint.tick is ESP32ProtocolSimulator.tick
            assert DeliveryEndpoint._respond is ESP32ProtocolSimulator._respond
            for method in (run.system.tick, run.system.pipeline.observe, run.system.pipeline.decision,
                           run.system.pipeline.command, run.owner._run):
                assert "/evidence/" not in Path(inspect.getfile(method)).as_posix()
            assert run.system.gnss_reader is None and run.system.esp32_transport is None
        finally:
            app.state.system.close()


@pytest.mark.parametrize("field", ["state", "sequence", "timestamp", "health", "session", "event"])
def test_digest_retains_deterministic_fields(reference, field):
    trace = deepcopy(reference["trace"])
    row = trace[0]
    if field == "state": row["decision"]["state"] = "STOP"
    elif field == "sequence": row["command"]["sequence"] += 1
    elif field == "timestamp": row["logical_runtime_time"] += 1
    elif field == "health": row["radar_health"]["freshness"] = "STALE"
    elif field == "session": row["client"]["session_id"] = "f"*48
    elif field == "event": row["event"]["reason"] = "WRONG"
    assert trace_digest(trace) != reference["digest"]


def test_digest_excludes_only_named_bookkeeping(reference):
    trace = deepcopy(reference["trace"])
    for row in trace:
        row["run_id"], row["scenario_id"], row["observer_reads"] = "another", "EV-99", {"bookkeeping": "different"}
    assert trace_digest(trace) == reference["digest"]


@pytest.mark.parametrize("field", ["left_command", "right_command", "permitted_speed_mps"])
def test_nonzero_command_tripwire(reference, field):
    row = deepcopy(reference["trace"][0])
    row["command"][field] = .001
    with pytest.raises(EvidenceFailure, match="NONZERO"): assert_zero(row)


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    destination = tmp_path_factory.mktemp("evidence-parent")/"package"
    result = build_bundle(destination, progress=lambda message: None)
    assert result["repetitions"] == 150
    return destination


def test_complete_package_and_no_overwrite(bundle):
    assert verify_bundle(bundle)["artifact_count"] == 85
    with pytest.raises(EvidenceFailure, match="already exists"): build_bundle(bundle)
    manifest = read_json(bundle/"manifest.json")
    assert manifest["hardware_access"] is False
    assert manifest["source_hash_normalization"] == "CRLF_TO_LF"
    assert all(b"\r\n" not in p.read_bytes() for p in bundle.rglob("*") if p.is_file())
    assert "Users/" not in json.dumps(manifest) and "Users\\" not in json.dumps(manifest)


@pytest.mark.parametrize("mutation", ["tamper", "missing", "extra", "nested_hashes", "rehash_trace", "wrong_config", "wrong_protocol", "missing_repeat", "observer", "replay", "source", "scenario"])
def test_artifact_negative_controls(bundle, tmp_path, mutation):
    target = tmp_path/"changed"
    shutil.copytree(bundle, target)
    if mutation == "missing": (target/"traces/EV-01.jsonl").unlink()
    elif mutation == "extra": write_json(target/"unlisted.json", {})
    elif mutation == "nested_hashes": write_json(target/"nested/hashes.json", {})
    elif mutation in {"tamper", "rehash_trace"}:
        path = target/"traces/EV-01.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        rows[0]["decision"]["state"] = "STOP"
        path.write_text("".join(json.dumps(row)+"\n" for row in rows))
    elif mutation in {"wrong_config", "wrong_protocol", "source"}:
        path = target/"manifest.json"
        value = read_json(path)
        value[{"wrong_config": "configuration_fingerprint", "wrong_protocol": "protocol_version", "source": "source_sha256"}[mutation]] = "WRONG"
        write_json(path, value)
    elif mutation == "missing_repeat":
        path = target/"runs/EV-01.json"
        write_json(path, read_json(path)[:-1])
    elif mutation == "observer":
        path = target/"evidence_summary.json"
        value = read_json(path); value["observer_digest"] = "WRONG"
        write_json(path, value)
    elif mutation == "replay":
        path = target/"replay/EV-01.json"
        value = read_json(path); value["records"][0]["payload"]["decision"]["D_env_m"] += 1
        write_json(path, value)
    elif mutation == "scenario":
        path = target/"scenarios/EV-01.json"
        value = read_json(path); value["steps"][0]["expect"]["sequence"] = 500
        write_json(path, value)
    if mutation not in {"tamper", "missing", "extra"}:
        # Rehashing alone cannot hide semantic/config/replay discrepancies.
        write_json(target/"hashes.json", inventory(target))
    with pytest.raises((EvidenceFailure, AssertionError)):
        verify_bundle(target)
