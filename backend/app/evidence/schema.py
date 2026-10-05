"""Closed, bounded scenario vocabulary. No executable expressions in inputs."""
from __future__ import annotations

import hashlib
import json
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = 1
SEED = 42
BASELINE = "96bf72bbfea88834c173000b271fd016b6b206e9"
EXCLUSIONS = frozenset({"run_id", "scenario_id", "observer_reads"})


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def trace_digest(trace: list[dict]) -> str:
    # Only these named TOP-LEVEL bookkeeping fields are excluded. In particular
    # no timestamp, session, health, command or safety field is recursively removed.
    return digest([{k: v for k, v in row.items() if k not in EXCLUSIONS} for row in trace])


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Report(Strict):
    age_ns: int = Field(default=0, ge=-1_000_000_000, le=9_000_000_000)
    candidate_id: int = Field(default=1, ge=0, le=100)
    distance_m: float = Field(default=3.0, ge=0, le=100)
    empty: bool = False


class Advance(Strict):
    pi_ns: int = Field(ge=0, le=10_000_000_000)
    receiver_ns: int = Field(ge=0, le=10_000_000_000)
    tick: bool = True


class Mutation(Strict):
    kind: Literal["late", "empty", "missing_sequence", "wrong_sequence", "wrong_session",
                  "wrong_config", "wrong_source", "malformed_cbor", "nack", "status"]


class NoArgs(Strict):
    pass


ARGUMENTS = {
    "ADVANCE_TIME": Advance, "RADAR_REPORT": Report, "INJECT_RESPONSE": Mutation,
    **{name: NoArgs for name in (
        "NO_REPORT", "DROP_COMMUNICATION", "RESTORE_COMMUNICATION", "RESTART_RECEIVER",
        "RESTART_SENDER", "OLD_COMMAND", "TRANSPORT_RECONNECT", "START_RECORDING",
        "STOP_RECORDING", "VERIFY_REPLAY")},
}
# Explicit assertion vocabulary, not arbitrary dotted lookups/eval.
FACT_TYPES = {
    "state": str, "freshness": str, "health_reason": str, "communication": str,
    "receiver_reason": str, "response_error": str, "replay": str,
    "sequence": int, "events": int, "tracks": int, "last_seen_ns": int,
    "pending": int, "invalid_feedback": int, "reports_consumed": int,
    "publication_available": bool, "receiver_active": bool, "session_active": bool,
    "transport_flushed": bool,
}


class Step(Strict):
    action: str
    args: dict = Field(default_factory=dict)
    expect: dict = Field(min_length=1)

    @model_validator(mode="after")
    def valid(self):
        if self.action not in ARGUMENTS:
            raise ValueError("unknown action")
        self.args = ARGUMENTS[self.action].model_validate(self.args).model_dump()
        for key, value in self.expect.items():
            if key not in FACT_TYPES or type(value) is not FACT_TYPES[key]:
                raise ValueError(f"unknown or wrongly typed expected fact: {key}")
        return self


class Scenario(Strict):
    scenario_id: str = Field(pattern=r"^EV-(0[1-9]|1[0-9]|20)$")
    title: str
    purpose: str
    initial_runtime_time: int = Field(default=10_000_000_000, gt=0)
    initial_receiver_time: int = Field(default=1_000_000_000, gt=0)
    configuration: Literal["config/phase1.json"] = "config/phase1.json"
    initial_reports: list[Report] = Field(max_length=16)
    record_from_start: bool = True
    observer_profile: Literal["none", "one_rest", "multi_rest_ws"] = "none"
    response_policy: Literal["deliver", "drop"] = "deliver"
    steps: list[Step] = Field(min_length=1, max_length=100)
    expected_final_state: Literal["NORMAL", "WARN", "RESTRICT", "UNKNOWN", "STOP"]
    repeat_count: int = Field(ge=5, le=10)
    expected_invariants: Literal["PHASE1_ZERO_NO_HARDWARE_NO_REPLAY_AUTHORITY"] = "PHASE1_ZERO_NO_HARDWARE_NO_REPLAY_AUTHORITY"

    @model_validator(mode="after")
    def ordering(self):
        active, stopped = self.record_from_start, False
        queued = len(self.initial_reports)
        for step in self.steps:
            if step.action == "START_RECORDING":
                if active or stopped:
                    raise ValueError("only one recording; cannot start twice")
                active = True
            elif step.action == "STOP_RECORDING":
                if not active:
                    raise ValueError("cannot stop inactive recording")
                active, stopped = False, True
            elif step.action == "VERIFY_REPLAY" and not stopped:
                raise ValueError("replay requires stopped recording")
            if step.action == "RADAR_REPORT":
                queued += 1
                if queued > 16:
                    raise ValueError("scenario exceeds production report queue")
            if step.action == "ADVANCE_TIME" and step.args["tick"]:
                queued = 0
        if active or not stopped or self.steps[-1].action != "VERIFY_REPLAY":
            raise ValueError("scenario must stop and verify recording")
        return self


def assert_expected(scenario: str, step: int, expected: dict, facts: dict):
    for key, value in expected.items():
        if facts[key] != value:
            raise AssertionError(f"{scenario} step {step} {key}: expected {value!r}, actual {facts[key]!r}")
