"""Independently authored expectations for existing Phase-1 behavior, not policy."""
from .schema import Scenario


def step(action, expect, **args):
    return {"action": action, "args": args, "expect": expect}


def advance(ms, expect, *, tick=True, receiver_ms=None):
    return step("ADVANCE_TIME", expect, pi_ns=ms*1_000_000,
                receiver_ns=(ms if receiver_ms is None else receiver_ms)*1_000_000, tick=tick)


def report(expect, **args):
    return step("RADAR_REPORT", expect, **args)


def catalog() -> list[Scenario]:
    cases = []

    def add(n, title, actions, final="NORMAL", initial=None, **options):
        repetitions = 10 if n in {1, 3, 4, 6, 10, 13, 16, 17, 18, 20} else 5
        cases.append(Scenario.model_validate({
            "scenario_id": f"EV-{n:02}", "title": title, "purpose": title,
            "initial_reports": [{}] if initial is None else initial,
            "steps": actions + [step("STOP_RECORDING", {"state": final}),
                                step("VERIFY_REPLAY", {"replay": "MATCH", "state": final})],
            "expected_final_state": final, "repeat_count": repetitions, **options,
        }))

    add(1, "Fresh input produces one recorded zero-output command per tick", [
        advance(100, {"state": "NORMAL", "freshness": "FRESH", "sequence": 2, "events": 2})])
    add(2, "AGING preserves the current provisional NORMAL semantics", [
        advance(500, {"state": "NORMAL", "freshness": "AGING"})])
    add(3, "Expired observation is not current NORMAL evidence", [
        advance(1100, {"publication_available": False}, tick=False),
        advance(0, {"state": "UNKNOWN", "freshness": "STALE"})], "UNKNOWN")
    add(4, "Queued old source timestamp is never refreshed by consumption", [
        report({"state": "UNKNOWN"}, age_ns=2_000_000_000),
        advance(0, {"state": "UNKNOWN", "freshness": "STALE", "last_seen_ns": 8_000_000_000})], "UNKNOWN", initial=[])
    add(5, "Future timestamp reaches production rejection", [
        report({"state": "NORMAL"}, age_ns=-1),
        advance(0, {"state": "UNKNOWN", "freshness": "STALE", "health_reason": "INVALID_OBSERVATION_TIMESTAMP"})], "UNKNOWN")
    add(6, "Explicit empty report is fresh observation without an envelope", [
        report({"state": "UNKNOWN"}, empty=True),
        advance(0, {"state": "STOP", "freshness": "FRESH", "tracks": 0, "reports_consumed": 1})], "STOP", initial=[])
    add(7, "No report remains missing rather than valid-empty", [
        step("NO_REPORT", {"freshness": "MISSING"}),
        advance(1100, {"state": "UNKNOWN", "freshness": "MISSING", "reports_consumed": 0})], "UNKNOWN", initial=[])
    add(8, "All reports in an ordered batch reach the pipeline and recording", [
        report({"state": "UNKNOWN"}, age_ns=100_000_000, distance_m=4.0),
        report({"state": "UNKNOWN"}, distance_m=2.0, candidate_id=2),
        advance(0, {"state": "NORMAL", "reports_consumed": 2, "tracks": 2})], initial=[])
    add(9, "Equal source timestamps preserve insertion order", [
        report({"state": "NORMAL"}, distance_m=5.0),
        report({"state": "NORMAL"}, distance_m=2.0),
        advance(0, {"state": "NORMAL", "reports_consumed": 2, "tracks": 1})])
    add(10, "Response loss degrades correlation and receiver expires without frames", [
        step("DROP_COMMUNICATION", {"communication": "ONLINE"}),
        advance(100, {"pending": 1, "receiver_active": True}),
        advance(600, {"pending": 0, "communication": "NOT_CONNECTED", "receiver_reason": "COMMAND_EXPIRED", "receiver_active": False}, tick=False)])
    add(11, "Late ACK cannot renew exchange health", [
        step("DROP_COMMUNICATION", {"communication": "ONLINE"}),
        advance(100, {"pending": 1}),
        advance(600, {"communication": "NOT_CONNECTED"}, tick=False),
        step("INJECT_RESPONSE", {"response_error": "RESPONSE_IDENTITY_MISMATCH", "communication": "NOT_CONNECTED"}, kind="late")])
    bad = [step("DROP_COMMUNICATION", {"communication": "ONLINE"}), advance(100, {"pending": 1})]
    for count, mutation in enumerate(("empty", "missing_sequence", "wrong_sequence", "wrong_session", "wrong_config", "wrong_source", "malformed_cbor"), 1):
        bad.append(step("INJECT_RESPONSE", {"invalid_feedback": count, "pending": 1}, kind=mutation))
    bad += [step("INJECT_RESPONSE", {"communication": "DEGRADED", "pending": 0}, kind="nack"),
            step("INJECT_RESPONSE", {"communication": "DEGRADED"}, kind="status"),
            advance(600, {"communication": "STALE"}, tick=False)]
    add(12, "Bad response schemas/identities do not validate exchange; NACK/STATUS semantics", bad)
    add(13, "Receiver reboot rejects old session and duplicate sequence", [
        step("OLD_COMMAND", {"receiver_reason": "DUPLICATE_SEQUENCE", "receiver_active": False}),
        step("RESTART_RECEIVER", {"receiver_reason": "NOT_ENABLED"}),
        step("OLD_COMMAND", {"receiver_reason": "NOT_ENABLED", "receiver_active": False}),
        step("RESTART_SENDER", {"session_active": False}),
        advance(100, {"communication": "ONLINE", "session_active": True}),
        step("OLD_COMMAND", {"receiver_reason": "SESSION_MISMATCH", "receiver_active": False})])
    add(14, "Sender-session reset retires outstanding authority", [
        step("DROP_COMMUNICATION", {"communication": "ONLINE"}),
        advance(100, {"pending": 1}),
        step("RESTART_SENDER", {"pending": 0, "session_active": False}),
        step("RESTORE_COMMUNICATION", {"communication": "NOT_CONNECTED"}),
        advance(100, {"communication": "ONLINE"}),
        step("OLD_COMMAND", {"receiver_reason": "SESSION_MISMATCH"})])
    add(15, "Production byte transport flushes partial RX and queued TX on reconnect", [
        step("TRANSPORT_RECONNECT", {"transport_flushed": True, "session_active": False}),
        advance(100, {"communication": "ONLINE"})])
    common = [advance(100, {"state": "NORMAL", "freshness": "FRESH"}),
              advance(400, {"state": "NORMAL", "freshness": "AGING"}),
              advance(600, {"state": "UNKNOWN", "freshness": "STALE"}),
              report({"state": "UNKNOWN"}), advance(0, {"state": "NORMAL", "freshness": "FRESH"})]
    for n, profile in ((16, "none"), (17, "one_rest"), (18, "multi_rest_ws")):
        add(n, f"Observer equivalence: {profile}", common, observer_profile=profile)
    add(19, "Recording begins from a live nonempty checkpoint", [
        advance(100, {"sequence": 2}), step("START_RECORDING", {"sequence": 2}),
        advance(100, {"sequence": 3}), advance(900, {"state": "UNKNOWN"})], "UNKNOWN", record_from_start=False)
    add(20, "Complete loss, expiry, session renewal, fresh recovery and replay story", [
        advance(500, {"freshness": "AGING", "state": "NORMAL"}),
        report({"state": "NORMAL"}, empty=True),
        advance(0, {"freshness": "FRESH", "state": "NORMAL"}),
        advance(1100, {"state": "UNKNOWN", "freshness": "STALE"}),
        step("DROP_COMMUNICATION", {"communication": "ONLINE"}),
        advance(100, {"pending": 1}),
        advance(600, {"communication": "NOT_CONNECTED", "receiver_reason": "COMMAND_EXPIRED"}, tick=False),
        step("TRANSPORT_RECONNECT", {"transport_flushed": True, "session_active": False}),
        step("RESTART_RECEIVER", {"receiver_active": False}),
        step("RESTORE_COMMUNICATION", {"communication": "NOT_CONNECTED"}),
        report({"state": "UNKNOWN"}),
        advance(0, {"state": "NORMAL", "freshness": "FRESH", "communication": "ONLINE"})])
    return cases
