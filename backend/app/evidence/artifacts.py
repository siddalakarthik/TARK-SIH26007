"""Portable, hash-inventoried evidence package; fingerprints are NOT signatures."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

from .catalog import catalog
from .controls import negative_controls
from .runner import EvidenceFailure, ROOT, assert_zero, run_scenario, settings
from .schema import BASELINE, SCHEMA_VERSION, SEED, Scenario, assert_expected, digest, trace_digest
from app.communication.esp32.protocol import VERSION
from app.replay.engine import replay_recording

NEGATIVES = {"replay_mismatch", "config_identifier", "config_values", "protocol_version", "opener_tripwire",
             "zero_output_tripwire", "deterministic_field_tamper", "wrong_expected_result", "storage_failure", "runtime_failure"}


def command(*args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=20)
    if result.returncode:
        raise EvidenceFailure(f"metadata command failed: {args[0]}")
    return result.stdout.strip()


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")


def read_json(path: Path):
    if path.stat().st_size > 5_000_000:
        raise EvidenceFailure("oversized evidence artifact")
    return json.loads(path.read_text(encoding="utf-8"))


def source_hashes():
    files = [*ROOT.glob("backend/app/**/*.py"), *ROOT.glob("backend/tests/*.py"),
             *ROOT.glob("firmware/esp32/**/*.c"), *ROOT.glob("firmware/esp32/**/*.h"),
             ROOT/"scripts/run_evidence_harness.py", ROOT/"config/phase1.json", ROOT/"protocol_vectors.json",
             ROOT/"pyproject.toml", ROOT/"frontend/package.json", ROOT/"docs/DETERMINISTIC_EVIDENCE_HARNESS_SPEC.md", ROOT/".gitattributes"]
    # All listed sources are text. Match the production replay fingerprint's
    # CRLF normalization so Git platform checkout does not change code identity.
    return {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest() for p in sorted(files)}


def make_manifest(scenarios):
    command("git", "merge-base", "--is-ancestor", BASELINE, "HEAD")
    compiler = shutil.which("gcc")
    if not compiler and Path("C:/msys64/ucrt64/bin/gcc.exe").is_file():
        compiler = "C:/msys64/ucrt64/bin/gcc.exe"
    config = settings()
    return {"project": "TARK SIH26007", "run_id": "prompt3-seed42", "schema_version": SCHEMA_VERSION,
            "generated_utc": datetime.now(timezone.utc).isoformat(), "required_baseline": BASELINE,
            "git_head": command("git", "rev-parse", "HEAD"), "git_branch": command("git", "branch", "--show-current"),
            "git_dirty": bool(command("git", "status", "--porcelain")),
            "source_sha256": source_hashes(), "source_hash_normalization": "CRLF_TO_LF", "protocol_version": VERSION,
            "configuration_identifier": config.configuration_hash,
            "configuration_fingerprint": digest(config.model_dump(mode="json", exclude={"mode"})),
            "scenario_fingerprint": digest([s.model_dump() for s in scenarios]),
            "seed": SEED, "python_version": platform.python_version(), "platform": platform.system(),
            "machine": platform.machine(), "packages": {p: version(p) for p in ("fastapi", "pydantic", "cbor2", "httpx", "pytest")},
            "compiler": None if not compiler else command(compiler, "--version").splitlines()[0],
            "application_version": "0.3.0", "source_mode": "TEST_FIXTURE", "runtime_mode": "REPLAY",
            "traction": "DISABLED_PHASE_1", "hardware_access": False, "physical_validation": False,
            "limitations": ["Host software evidence, not physical validation or certification.",
                "Radar reports use the existing normalized queue, not physical frames.",
                "Production REAL queue labels inside records denote an input boundary; these records are TEST_FIXTURE.",
                "Hash inventory is not a signature or proof against deliberate wholesale replacement.",
                "Pre-commit HEAD and dirty status are recorded; source hashes identify bytes used.",
                "Durations are host diagnostics, not WCET or embedded timing guarantees."]}


def inventory(directory: Path):
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink(): raise EvidenceFailure("symlinks forbidden in evidence")
        if not path.is_file() or path == directory/"hashes.json": continue
        data = path.read_bytes()
        files[path.relative_to(directory).as_posix()] = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
    return files


def build_bundle(directory: Path, progress=print):
    if directory.exists(): raise EvidenceFailure("output already exists; choose a fresh directory")
    scenarios = catalog()
    manifest = make_manifest(scenarios)
    directory.mkdir(parents=True)
    write_json(directory/"manifest.json", manifest)
    results = []
    reference = None
    for scenario in scenarios:
        sid = scenario.scenario_id
        write_json(directory/"scenarios"/(sid+".json"), scenario.model_dump())
        repetitions, representative = [], None
        for iteration in range(1, scenario.repeat_count+1):
            result = run_scenario(scenario, f"{sid}-{iteration:02}")
            if representative is None: representative = result
            if result["digest"] != representative["digest"]:
                raise EvidenceFailure(f"NONDETERMINISM {sid} repetition {iteration}")
            repetitions.append({k: v for k, v in result.items() if k not in {"trace", "replay"}})
        if sid == "EV-01": reference = representative
        path = directory/"traces"/(sid+".jsonl")
        path.parent.mkdir(exist_ok=True)
        path.write_text("".join(json.dumps(row, sort_keys=True, allow_nan=False)+"\n" for row in representative["trace"]), encoding="utf-8", newline="\n")
        write_json(directory/"replay"/(sid+".json"), representative["replay"])
        write_json(directory/"runs"/(sid+".json"), repetitions)
        results.append({"scenario_id": sid, "result": "PASS", "repetitions": len(repetitions),
                        "digest": representative["digest"], "counts": representative["counts"],
                        "duration_s_total": round(sum(r["host_duration_s"] for r in repetitions), 6)})
        progress(f"{sid}: PASS ({len(repetitions)} independent repetitions)")
    observers = [r["digest"] for r in results if r["scenario_id"] in {"EV-16", "EV-17", "EV-18"}]
    if len(set(observers)) != 1: raise EvidenceFailure("observer-dependent logical trace")
    write_json(directory/"negative_controls.json", negative_controls(reference))
    write_json(directory/"evidence_summary.json", {"result": "PASS", "scenario_count": len(results),
        "repetitions": sum(r["repetitions"] for r in results), "scenarios": results,
        "observer_equivalence": "MATCH", "observer_digest": observers[0],
        "hardware_access": False, "physical_validation": False, "traction": "DISABLED_PHASE_1",
        "all_shutdowns_complete": True, "new_production_defects": [],
        "performance_note": "Host durations/counts/bytes only. No real-time or physical timing claim."})
    (directory/"README.md").write_text(
        "# Prompt-3 deterministic software evidence\n\n"
        "TEST_FIXTURE; no hardware accessed, no physical validation. Traction DISABLED_PHASE_1.\n\n"
        "From repository root, use `python scripts/run_evidence_harness.py --output <fresh-directory>`; "
        "verify with `python scripts/run_evidence_harness.py --verify <directory>`. Use the existing project environment. "
        "Unset inherited TARK_* configuration; only TARK_DATABASE_PATH=:memory: is permitted. "
        "No network, sensor devices or package installation is required.\n\n"
        "Manifest fingerprints identify source/configuration/tool versions. Text source hashes normalize CRLF to LF; "
        "artifact hashes cover exact bytes and exports use LF. Runs contain all 150 repeat results; "
        "traces and replay contain one full representative per scenario. Replay exports retain UUIDs; "
        "logical traces omit event/storage UUIDs at named projections. Only top-level run_id, scenario_id and "
        "observer_reads are excluded from the logical digest. All controlled times, sessions, health, decisions, "
        "events, commands and sequences remain included. Observer reads have separate before/after authority checks.\n\n"
        "A trace's decision is the LAST GENERATED decision. publication_available=false explicitly means it is "
        "not current evidence; clock-only fault steps deliberately show this distinction. Protocol snapshot fields "
        "are last-tick values; client/receiver/communication_health record current controlled time. "
        "wire_commands includes deliberately re-injected old frames; command_submissions counts actual production submit calls.\n\n"
        "The replay-mode normalized queue retains the application's REAL boundary label internally; every input here "
        "is a TEST_FIXTURE, not real radar. The in-process receiver uses production Python protocol/supervision code. "
        "Fresh C host/interoperability regression is separately recorded in the report.\n\n"
        "Hashes cover every artifact except hashes.json itself. They detect changes, not provenance against a party "
        "replacing the entire package. The verifier also checks semantics, expected outcomes and replay. "
        "Host durations are not WCET. Pre-commit source hashes avoid claiming a self-referential commit identity.\n",
        encoding="utf-8", newline="\n")
    write_json(directory/"hashes.json", inventory(directory))
    return verify_bundle(directory)


def verify_bundle(directory: Path, *, verify_sources=True):
    scenarios = catalog()
    required = {"manifest.json", "evidence_summary.json", "negative_controls.json", "README.md"}
    for s in scenarios:
        required |= {f"{folder}/{s.scenario_id}.{suffix}" for folder, suffix in
                     (("scenarios", "json"), ("runs", "json"), ("traces", "jsonl"), ("replay", "json"))}
    supplied, actual = read_json(directory/"hashes.json"), inventory(directory)
    if set(actual) != required or supplied != actual:
        raise EvidenceFailure("artifact inventory/hash mismatch (missing, extra or tampered artifact)")
    manifest = read_json(directory/"manifest.json")
    config = settings()
    if manifest["protocol_version"] != VERSION or manifest["schema_version"] != SCHEMA_VERSION:
        raise EvidenceFailure("unsupported evidence/protocol version")
    if manifest["configuration_identifier"] != config.configuration_hash or manifest["configuration_fingerprint"] != digest(config.model_dump(mode="json", exclude={"mode"})):
        raise EvidenceFailure("configuration identity mismatch")
    if manifest.get("source_hash_normalization") != "CRLF_TO_LF":
        raise EvidenceFailure("unsupported source hash normalization")
    if verify_sources and manifest["source_sha256"] != source_hashes():
        raise EvidenceFailure("source fingerprint mismatch")
    if manifest["scenario_fingerprint"] != digest([s.model_dump() for s in scenarios]):
        raise EvidenceFailure("scenario fingerprint mismatch")
    for data in (manifest, read_json(directory/"evidence_summary.json")):
        if data["hardware_access"] is not False or data["physical_validation"] is not False or data["traction"] != "DISABLED_PHASE_1":
            raise EvidenceFailure("invalid safety/maturity claims")
    summary = read_json(directory/"evidence_summary.json")
    if summary["result"] != "PASS" or summary["scenario_count"] != 20 or summary["repetitions"] != 150:
        raise EvidenceFailure("incomplete scenario summary")
    if [r["scenario_id"] for r in summary["scenarios"]] != [s.scenario_id for s in scenarios]:
        raise EvidenceFailure("scenario summary coverage mismatch")
    for s, aggregate in zip(scenarios, summary["scenarios"]):
        sid = s.scenario_id
        parsed = Scenario.model_validate(read_json(directory/"scenarios"/(sid+".json")))
        if parsed != s: raise EvidenceFailure("scenario differs from approved catalog")
        trace = [json.loads(line) for line in (directory/"traces"/(sid+".jsonl")).read_text(encoding="utf-8").splitlines()]
        if len(trace) != len(s.steps)+1: raise EvidenceFailure("truncated trace")
        logical = trace_digest(trace)
        runs = read_json(directory/"runs"/(sid+".json"))
        if len(runs) != s.repeat_count or aggregate["repetitions"] != s.repeat_count:
            raise EvidenceFailure("missing repetition")
        if aggregate["digest"] != logical or aggregate["result"] != "PASS":
            raise EvidenceFailure("trace/summary digest disagreement")
        for i, run in enumerate(runs, 1):
            if run["digest"] != logical or run["result"] != "PASS" or run["run_id"] != f"{sid}-{i:02}" or run["scenario_id"] != sid or run["seed"] != SEED:
                raise EvidenceFailure("repetition/digest disagreement")
            if run["hardware_opener_calls"] != 0 or run["shutdown_complete"] is not True:
                raise EvidenceFailure("failed isolation/shutdown")
            if run["counts"] != trace[-1]["counts"] or aggregate["counts"] != run["counts"]:
                raise EvidenceFailure("inconsistent repetition counts")
        for index, row in enumerate(trace):
            if row["step_number"] != index or row["scenario_id"] != sid or row["source"] != "TEST_FIXTURE":
                raise EvidenceFailure("invalid trace identity/order")
            assert_zero(row)
            if row["observer_reads"]["before"] != row["observer_reads"]["after"]:
                raise EvidenceFailure("observer authority altered")
            if row["counts"]["ticks"] != row["counts"]["events"] or row["counts"]["ticks"] != row["counts"]["command_submissions"]:
                raise EvidenceFailure("one-command/event per tick violated")
            if index:
                step = s.steps[index-1]
                if row["action"] != step.action or row["args"] != step.args:
                    raise EvidenceFailure("trace action mismatch")
                assert_expected(sid, index, step.expect, row["facts"])
        if trace[-1]["facts"]["state"] != s.expected_final_state:
            raise EvidenceFailure("wrong final state")
        replay = read_json(directory/"replay"/(sid+".json"))
        result = replay_recording(replay["records"], config, replay["session"])
        if result.result != "MATCH" or replay["result"]["result"] != "MATCH" or trace[-1]["replay"]["result"] != "MATCH":
            raise EvidenceFailure("replay mismatch")
        if trace[-1]["replay"]["live_before"] != trace[-1]["replay"]["live_after"]:
            raise EvidenceFailure("replay changed live authority")
    negative = read_json(directory/"negative_controls.json")
    if set(negative) != NEGATIVES or any(v["result"] != "PASS" for v in negative.values()):
        raise EvidenceFailure("negative controls incomplete")
    observer_digests = [r["digest"] for r in summary["scenarios"] if r["scenario_id"] in {"EV-16", "EV-17", "EV-18"}]
    if len(set(observer_digests)) != 1 or summary["observer_digest"] != observer_digests[0] or summary["observer_equivalence"] != "MATCH":
        raise EvidenceFailure("observer trace mismatch")
    return {"result": "PASS", "scenarios": 20, "repetitions": 150,
            "artifact_count": len(actual)+1, "artifact_bytes": sum(x["bytes"] for x in actual.values()),
            "observer_equivalence": "MATCH"}
