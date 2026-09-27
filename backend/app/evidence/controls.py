"""Deliberate negative controls; mutations only affect fixture data/boundaries."""
from copy import deepcopy
import asyncio
import json
import sqlite3
from .schema import Scenario, trace_digest
from .catalog import catalog
from .runner import (ControlledRun, EvidenceFailure, HardwareTripwire, ROOT,
                     assert_zero, isolated_environment, settings)
from app.replay.engine import replay_recording, ReplayConfigurationError
from app.communication.esp32.protocol import decode_frame, ProtocolError


def failure_publication(kind):
    """Fail an external storage/scheduling boundary, not the decision algorithm."""
    with isolated_environment():
        from app.main import create_app, DeploymentConfig
        from fastapi.testclient import TestClient
        run = ControlledRun(catalog()[0], "negative-"+kind)
        app = create_app(settings(), DeploymentConfig(), runtime_factory=run.factory)
        evidence = None
        exception_type = sqlite3.OperationalError if kind == "storage" else RuntimeError
        try:
            with TestClient(app) as client:
                before = run.authority()
                if kind == "storage":
                    run.system.event_store.db.execute("PRAGMA query_only=ON")
                    try:
                        client.portal.call(run.release_tick)
                    except sqlite3.OperationalError:
                        pass
                else:
                    async def fail_worker():
                        await run.queue.put(RuntimeError("CONTROLLED_SCHEDULER_FAILURE"))
                        for _ in range(100):
                            await asyncio.sleep(0)
                            if run.owner.task.done(): return
                        raise EvidenceFailure("failure was not observed")
                    client.portal.call(fail_worker)
                if not run.owner.task.done(): raise EvidenceFailure("worker still running")
                actual_error = run.owner.task.exception()
                if not isinstance(actual_error, exception_type): raise EvidenceFailure("wrong injected error")
                after = run.authority()
                if before != after: raise EvidenceFailure("failure increased command/transport capability")
                status, ready = client.get("/api/v1/status"), client.get("/ready")
                if status.status_code != 503 or ready.status_code != 503 or run.publication_available():
                    raise EvidenceFailure("failed worker retained current-looking publication")
                assert_zero(run.owner._snapshot)
                evidence = {"result": "PASS", "error_type": type(actual_error).__name__,
                            "status_http": status.status_code, "ready_http": ready.status_code,
                            "live_authority_unchanged": before == after, "last_output_zero": True}
        except exception_type as error:
            # The existing lifespan intentionally propagates the worker failure.
            if evidence is None or error is not actual_error: raise
        else:
            raise EvidenceFailure("worker failure was suppressed at shutdown")
        return evidence


def negative_controls(reference):
    output = {}
    portable = reference["replay"]
    changed = deepcopy(portable["records"])
    changed[-1]["payload"]["decision"]["D_env_m"] += .125
    mismatch = replay_recording(changed, settings(), portable["session"])
    if mismatch.result != "MISMATCH" or mismatch.first_divergence != len(changed)-1:
        raise EvidenceFailure("replay mismatch negative control did not fail")
    output["replay_mismatch"] = {"result": "PASS", "observed": mismatch.result, "first_divergence": mismatch.first_divergence}
    for name, mutation in (("identifier", "configuration_hash"), ("values", "configuration_fingerprint")):
        session = deepcopy(portable["session"])
        if name == "identifier": session[mutation] = "WRONG_TEST_CONFIGURATION"
        else: session["metadata"][mutation] = "f"*64
        try: replay_recording(portable["records"], settings(), session)
        except ReplayConfigurationError as error:
            output["config_"+name] = {"result": "PASS", "rejected": str(error)}
        else: raise EvidenceFailure("wrong configuration accepted")
    vectors = json.loads((ROOT/"protocol_vectors.json").read_text())
    legacy = next(v for v in vectors if v["name"] == "legacy_version")
    try: decode_frame(bytes.fromhex(legacy["frame_hex"]))
    except ProtocolError as error:
        if error.reason != "unsupported protocol version": raise
        output["protocol_version"] = {"result": "PASS", "rejected": error.reason}
    else: raise EvidenceFailure("legacy protocol accepted")
    guard = HardwareTripwire()
    try: guard.deny()
    except EvidenceFailure:
        output["opener_tripwire"] = {"result": "PASS", "deliberate_calls_blocked": guard.calls}
    else: raise EvidenceFailure("tripwire not active")
    row = deepcopy(reference["trace"][0])
    row["command"]["left_command"] = .1
    try: assert_zero(row)
    except EvidenceFailure:
        output["zero_output_tripwire"] = {"result": "PASS", "nonzero_fixture_rejected": True}
    else: raise EvidenceFailure("nonzero output accepted")
    changed_trace = deepcopy(reference["trace"])
    changed_trace[0]["decision"]["state"] = "STOP"
    if trace_digest(changed_trace) == reference["digest"]: raise EvidenceFailure("digest hides safety field")
    output["deterministic_field_tamper"] = {"result": "PASS", "digest_changed": True}
    wrong_expectation = catalog()[0].model_dump()
    wrong_expectation["steps"][0]["expect"]["sequence"] = 900
    from .runner import run_scenario
    try: run_scenario(Scenario.model_validate(wrong_expectation))
    except AssertionError as error:
        if "expected 900" not in str(error): raise
        output["wrong_expected_result"] = {"result": "PASS", "rejected": str(error)}
    else: raise EvidenceFailure("wrong expected result passed")
    output["storage_failure"] = failure_publication("storage")
    output["runtime_failure"] = failure_publication("worker")
    return output
