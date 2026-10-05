"""Deterministic external-boundary driver of the existing application lifespan."""
from __future__ import annotations

import asyncio
from contextlib import contextmanager, ExitStack
from copy import deepcopy
from dataclasses import asdict
import importlib.abc
import json
import os
from pathlib import Path
import struct
import sys
import time
from unittest.mock import Mock, patch

from app.config import Settings
from app.domain.models import RadarDetection
from app.communication.esp32.protocol import (
    ACK, NACK, STATUS, COMMAND, HEADER, ESP32Client, ESP32ProtocolSimulator,
    ProtocolError, cobs_encode, crc32c, decode_frame, encode_message,
)
from app.communication.esp32.serial_transport import BidirectionalSerialTransport
from app.replay.engine import replay_recording
from app.services.runtime import RuntimeOwner, RuntimeUnavailable
from .schema import SEED, Scenario, assert_expected, digest, trace_digest

ROOT = Path(__file__).resolve().parents[3]


class EvidenceFailure(AssertionError):
    pass


class HardwareTripwire(importlib.abc.MetaPathFinder):
    def __init__(self):
        self.calls = 0

    def deny(self, *args, **kwargs):
        self.calls += 1
        raise EvidenceFailure("PHYSICAL_BOUNDARY_TRIPWIRE")

    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"serial", "cv2", "board", "busio", "picamera2", "adafruit_bno055", "adafruit_mlx90640"}:
            self.deny()
        return None


@contextmanager
def isolated_environment():
    # Fail closed, not silently clear a real configuration. The launcher may
    # explicitly choose a fresh environment before calling this API.
    unsafe = [k for k, v in os.environ.items() if k.startswith("TARK_") and v
              and not (k == "TARK_DATABASE_PATH" and v == ":memory:")]
    if unsafe:
        raise EvidenceFailure("non-isolated TARK environment: " + ", ".join(sorted(unsafe)))
    previous = os.environ.get("TARK_DATABASE_PATH")
    guard = HardwareTripwire()
    os.environ["TARK_DATABASE_PATH"] = ":memory:"
    sys.meta_path.insert(0, guard)
    try:
        from app.services import system as system_module
        with ExitStack() as stack:
            for cls, method in (
                (system_module.GnssReader, "start"),
                (system_module.PiUvcCameraAdapter, "start"),
                (system_module.Bno055Adapter, "start_verified_sensor"),
                (system_module.Mlx90640Adapter, "start_verified_sensor"),
                (system_module.LD2450RawCaptureWorker, "start"),
                (system_module.IdentityGatedESP32UsbTransport, "open"),
            ):
                stack.enter_context(patch.object(cls, method, guard.deny))
            yield guard
            if guard.calls:
                raise EvidenceFailure("physical boundary was attempted")
    finally:
        sys.meta_path.remove(guard)
        if previous is None:
            os.environ.pop("TARK_DATABASE_PATH", None)
        else:
            os.environ["TARK_DATABASE_PATH"] = previous


def settings() -> Settings:
    value = Settings.from_file(ROOT / "config/phase1.json")
    if value.hard_cap_mps != 0:
        raise EvidenceFailure("Phase-1 zero-cap configuration required")
    return value.model_copy(update={"mode": "replay"})


def assert_zero(snapshot: dict):
    if snapshot["traction"] != "DISABLED_PHASE_1":
        raise EvidenceFailure("TRACTION_TRIPWIRE")
    command = snapshot["command"]
    if any(command[k] != 0 for k in ("permitted_speed_mps", "left_command", "right_command")) or snapshot["decision"]["permitted_speed_mps"] != 0:
        raise EvidenceFailure("NONZERO_OUTPUT_TRIPWIRE")
    feedback = snapshot["protocol"].get("feedback")
    if feedback:
        p = feedback["payload"]
        if p["output_state"] != "DISABLED_PHASE_1" or p.get("applied_left", 0) != 0 or p.get("applied_right", 0) != 0:
            raise EvidenceFailure("RECEIVER_OUTPUT_TRIPWIRE")


def bounded_ws_json(socket):
    # Starlette's synchronous receive has no timeout parameter. Bound its
    # existing ASGI receive stream, without another WS implementation.
    async def receive():
        return await asyncio.wait_for(socket._send_rx.receive(), timeout=5)
    message = socket.portal.call(receive)
    if message.get("type") != "websocket.send" or "text" not in message:
        raise EvidenceFailure("unexpected/closed observer WebSocket")
    return json.loads(message["text"])


class DeliveryEndpoint(ESP32ProtocolSimulator):
    """Only delivery/reboot is controlled. All decoding/supervision is inherited."""
    def __init__(self, config, clock):
        self.writes = []
        self.responses = []
        self.command_frames = []
        self.drop = False
        self.boot_number = 0
        self.delivery_clock = clock
        self.reboot(config)

    def reboot(self, config=None):
        self.boot_number += 1
        ESP32ProtocolSimulator.__init__(self, config or self.configuration_hash,
            clock=self.delivery_clock, boot_id=digest([SEED, "boot", self.boot_number])[:32])

    def write(self, frame):
        self.writes.append(frame)
        message, _ = decode_frame(frame)
        if message == COMMAND:
            self.command_frames.append(frame)
        super().write(frame)
        if self.last_response is not None:
            self.responses.append(self.last_response)
        if self.drop:
            self.last_response = None


class CaptureBoundary:
    """Normalized queue input, NOT an LD2450 decoder or a physical receiver."""
    def __init__(self):
        self.count, self.stamp = 0, None

    def diagnostics(self):
        return {"decoded_report_count": self.count, "last_timestamp_ns": self.stamp,
                "state": "ONLINE" if self.count else "NOT_CONNECTED", "reason": "TEST_FIXTURE",
                "rejected_frame_count": 0}

    def close(self):
        pass


class ControlledRun:
    def __init__(self, scenario: Scenario, run_id: str):
        self.scenario, self.run_id = scenario, run_id
        self.pi, self.receiver = scenario.initial_runtime_time, scenario.initial_receiver_time
        self.queue = asyncio.Queue()
        self.trace = []
        self.queued_reports, self.last_reports = [], []
        self.session = self.portable = self.replay_result = None
        self.response_error = ""
        self.transport_result = None
        self.nonce_count = 0

    def nonce(self):
        self.nonce_count += 1
        return digest([SEED, "nonce", self.nonce_count])[:32]

    def factory(self, system):
        self.system = system
        if system.hardware_runtime_requested:
            raise EvidenceFailure("hardware runtime forbidden")
        self.capture = CaptureBoundary()
        system.ld2450_capture = self.capture
        self.endpoint = DeliveryEndpoint(system.settings.configuration_hash, lambda: self.receiver)
        self.endpoint.drop = self.scenario.response_policy == "drop"
        system.esp32_endpoint = self.endpoint
        system.esp32_client = ESP32Client(self.endpoint, clock=lambda: self.pi, nonce_factory=self.nonce)
        # Observational counter only: delegates every call to the unchanged
        # production method. Replay must not invoke it, even if writes fail.
        self.submit_probe = Mock(wraps=system.esp32_client.submit)
        system.esp32_client.submit = self.submit_probe
        self.owner = RuntimeOwner(system, clock=lambda: self.pi, wait=self.wait)
        for report in self.scenario.initial_reports:
            self.feed(report.model_dump())
        self.last_reports, self.queued_reports = self.queued_reports, []
        if self.scenario.record_from_start:
            self.session = system.start_recording(self.pi)
        return self.owner

    async def wait(self, delay):
        if delay != RuntimeOwner.INTERVAL_S:
            raise EvidenceFailure("unexpected runtime schedule")
        value = await self.queue.get()
        if isinstance(value, Exception):
            raise value

    async def release_tick(self):
        before = self.system.pipeline.sequence
        await self.queue.put(True)
        for _ in range(100):
            await asyncio.sleep(0)
            if self.owner.task.done():
                self.owner.task.result()
                raise EvidenceFailure("runtime ended unexpectedly")
            if self.system.pipeline.sequence == before + 1:
                assert_zero(self.owner._snapshot)
                if self.counts()["events"] != self.system.pipeline.sequence:
                    raise EvidenceFailure("one-event-per-tick invariant failed")
                return
        raise EvidenceFailure("controlled tick did not complete")

    def feed(self, args):
        stamp = self.pi - args["age_ns"]
        detections = [] if args["empty"] else [RadarDetection(candidate_id=args["candidate_id"],
            timestamp_ns=stamp, x_m=args["distance_m"], y_m=0, velocity_mps=-1,
            quality=.9, uncertainty_m=.2)]
        self.system.ingest_ld2450_report(stamp, detections)
        self.capture.count += 1
        self.capture.stamp = stamp
        self.queued_reports.append({"timestamp_ns": stamp, "detections": [x.model_dump(mode="json") for x in detections]})

    def counts(self):
        return {"ticks": self.system.pipeline.sequence,
                "events": self.system.event_store.db.execute("SELECT count(*) FROM events").fetchone()[0],
                "command_submissions": self.submit_probe.call_count,
                "wire_commands": len(self.endpoint.command_frames), "wire_writes": len(self.endpoint.writes),
                "location_steps": self.system._location_step,
                "session_generation": self.endpoint.generation, "session_id": self.system.esp32_client.session_id}

    def authority(self):
        return {**self.counts(), "pending": list(self.system.esp32_client.pending),
                "last_sequence": self.system.esp32_client.last_sequence,
                "terminal": list(self.system.esp32_client.terminal)}

    def observe(self, client):
        profile = self.scenario.observer_profile
        before = self.authority()
        reads = []
        if profile != "none":
            for _ in range(1 if profile == "one_rest" else 3):
                for path in ("status", "tracks", "sensors", "events", "vehicle-location"):
                    response = client.get("/api/v1/" + path)
                    expected = 200 if self.publication_available() else 503
                    if response.status_code != expected:
                        raise EvidenceFailure(f"observer {path} returned {response.status_code}, expected {expected}")
                    if path == "status" and expected == 200:
                        if response.json()["command"]["sequence"] != before["ticks"]:
                            raise EvidenceFailure("REST observed a different decision step")
                    reads.append({"path": path, "status": response.status_code})
            if profile == "multi_rest_ws" and self.publication_available():
                for cycle in range(2):
                    with ExitStack() as sockets:
                        connections = [sockets.enter_context(client.websocket_connect("/api/v1/ws")) for _ in range(3)]
                        for socket in connections:
                            messages = [bounded_ws_json(socket), bounded_ws_json(socket)]
                            status = next(m for m in messages if m["type"] == "status")
                            if status["payload"]["command"]["sequence"] != before["ticks"]:
                                raise EvidenceFailure("WS observer changed/received a different step")
                            reads.append({"websocket_cycle": cycle, "types": [m["type"] for m in messages]})
        after = self.authority()
        if before != after:
            raise EvidenceFailure("OBSERVER_AUTHORITY_TRIPWIRE")
        return {"before": before, "after": after, "reads": reads}

    def publication_available(self):
        try:
            self.owner.latest()
            return True
        except RuntimeUnavailable:
            return False

    def inject_response(self, kind):
        client = self.system.esp32_client
        raw = next(frame for frame in reversed(self.endpoint.responses) if decode_frame(frame)[0] == ACK)
        _, envelope = decode_frame(raw)
        p, q, stamp = deepcopy(envelope["payload"]), envelope["sequence"], envelope["timestamp_ns"]
        message = ACK
        before = client.last_exchange_ns
        if kind == "empty": p = {}
        elif kind == "wrong_sequence": q += 100
        elif kind == "wrong_session": p["session_id"] = "f" * 48
        elif kind == "wrong_config": p["configuration_hash"] = "WRONG_TEST_CONFIG"
        elif kind == "wrong_source": p["source_mode"] = "REAL"
        elif kind == "nack":
            message, p["accepted"], p["reason"] = NACK, False, "NOT_ENABLED"
        elif kind == "status":
            message, stamp = STATUS, self.receiver
            p = {k: v for k, v in p.items() if k not in {"accepted", "applied_left", "applied_right"}}
            p["reason"] = "NONE"
        raw = encode_message(message, q, stamp, p)
        if kind in {"missing_sequence", "malformed_cbor"}:
            # Corrupt an external frame, not a second decoder. Valid CRC ensures
            # malformed CBOR is rejected at CBOR validation, not at CRC first.
            from app.communication.esp32.protocol import cobs_decode
            body = cobs_decode(raw[1:-1])[:-4]
            body = body[:8] if kind == "missing_sequence" else body[:HEADER.size] + b"\xff" + body[HEADER.size+1:]
            raw = b"\0" + cobs_encode(body + struct.pack("!I", crc32c(body))) + b"\0"
        self.response_error = ""
        try:
            feedback = client.receive(raw, self.pi)
            if kind not in {"nack", "status"}:
                raise EvidenceFailure("invalid response accepted")
            if feedback is None:
                raise EvidenceFailure("missing valid fault/telemetry response")
        except ProtocolError as error:
            if kind in {"nack", "status"}:
                raise
            self.response_error = error.reason
        if kind != "nack" and client.last_exchange_ns != before:
            raise EvidenceFailure("bad response or STATUS renewed exchange health")

    def reconnect(self):
        class FakePort:
            def __init__(self): self.written, self.closed = bytearray(), False
            def read(self, size): return b""
            def write(self, raw): self.written.extend(raw[:3]); return min(3, len(raw))
            def close(self): self.closed = True
        ports = [FakePort(), FakePort()]
        iterator = iter(ports)
        transport = BidirectionalSerialTransport(lambda: next(iterator), lambda frame: None,
            on_reset=self.system.esp32_client.reset_session, clock=lambda: self.pi)
        try:
            if not transport._connect(): raise EvidenceFailure("fake transport failed")
            # Session-open has a bounded local transmit deadline even if an old
            # command is already expired at this point in EV-20.
            frame = self.endpoint.writes[0]
            transport.write(frame)
            cut = len(frame)//2
            assert transport._frames.feed(frame[:cut]) == []
            queued = transport._tx.qsize()
            transport._close_serial()
            if not transport._connect(): raise EvidenceFailure("fake reconnect failed")
            tail = transport._frames.feed(frame[cut:])
            flushed = transport._tx.qsize() == 0 and not tail and ports[0].closed
            transport.write(frame)
            transport._write_one(ports[1])
            self.transport_result = {"queued_before": queued, "queued_after": transport._tx.qsize(),
                "old_port_bytes": len(ports[0].written), "new_port_bytes": len(ports[1].written),
                "flushed": flushed, "new_frame_exact": bytes(ports[1].written) == frame,
                "generation": transport._generation, "tx_dropped": transport.diagnostics.tx_dropped}
            if not flushed or not self.transport_result["new_frame_exact"]:
                raise EvidenceFailure("TRANSPORT_RECONNECT_TRIPWIRE")
        finally:
            transport.close()

    def act(self, step, client):
        action, args = step.action, step.args
        if action == "ADVANCE_TIME":
            self.pi += args["pi_ns"]
            self.receiver += args["receiver_ns"]
            self.endpoint.tick(self.receiver)
            if args["tick"]:
                self.last_reports, self.queued_reports = self.queued_reports, []
                client.portal.call(self.release_tick)
            else:
                self.system.esp32_client.expire_pending(self.pi)
        elif action == "RADAR_REPORT": self.feed(args)
        elif action == "NO_REPORT": pass
        elif action == "DROP_COMMUNICATION": self.endpoint.drop = True
        elif action == "RESTORE_COMMUNICATION": self.endpoint.drop = False
        elif action == "INJECT_RESPONSE": self.inject_response(args["kind"])
        elif action == "RESTART_RECEIVER": self.endpoint.reboot()
        elif action == "RESTART_SENDER": self.system.esp32_client.reset_session()
        elif action == "OLD_COMMAND": self.endpoint.write(self.endpoint.command_frames[0])
        elif action == "TRANSPORT_RECONNECT": self.reconnect()
        elif action == "START_RECORDING": self.session = self.system.start_recording(self.pi)
        elif action == "STOP_RECORDING": self.session = self.system.stop_recording(self.pi)
        elif action == "VERIFY_REPLAY":
            records = list(self.system.recording_store.iter_records(self.session["session_id"]))
            before = self.authority()
            result = replay_recording(iter(records), self.system.settings, self.session)
            after = self.authority()
            if before != after: raise EvidenceFailure("REPLAY_AUTHORITY_TRIPWIRE")
            if result.result != "MATCH": raise EvidenceFailure("production replay mismatch")
            self.replay_result = {**asdict(result), "live_before": before, "live_after": after}
            self.portable = {"source": "TEST_FIXTURE", "session": self.session, "records": records, "result": asdict(result)}
        else: raise EvidenceFailure("unimplemented scenario action")

    def row(self, number, action, args, observers):
        snapshot = self.owner._snapshot
        assert_zero(snapshot)
        if self.endpoint.output_state != "DISABLED_PHASE_1":
            raise EvidenceFailure("RECEIVER_OUTPUT_TRIPWIRE")
        health = self.system.pipeline.health(self.pi).model_dump(mode="json")
        link = self.system.esp32_client.health(self.pi)
        c = self.system.esp32_client
        current_session = None if self.session is None else self.system.recording_session(self.session["session_id"])
        facts = {"state": snapshot["decision"]["state"], "freshness": health["freshness"],
            "health_reason": health["reason"], "communication": link["state"], "receiver_reason": self.endpoint.last_reason,
            "response_error": self.response_error, "replay": "NOT_RUN" if self.replay_result is None else self.replay_result["result"],
            "sequence": snapshot["command"]["sequence"], "events": self.counts()["events"], "tracks": len(snapshot["tracks"]),
            "last_seen_ns": health["last_seen_ns"], "pending": len(c.pending), "invalid_feedback": c.invalid_feedback,
            "reports_consumed": len(self.last_reports), "publication_available": self.publication_available(),
            "receiver_active": self.endpoint.local_expiry_ns is not None, "session_active": c.session_id is not None,
            "transport_flushed": bool(self.transport_result and self.transport_result["flushed"])}
        return {"schema_version": 1, "run_id": self.run_id, "scenario_id": self.scenario.scenario_id,
            "step_number": number, "action": action, "args": args, "source": "TEST_FIXTURE",
            "logical_runtime_time": self.pi, "receiver_time": self.receiver, "facts": facts,
            "last_tick_reports": deepcopy(self.last_reports), "queued_reports": deepcopy(self.queued_reports),
            "last_generated_snapshot_time": snapshot["timestamp_ns"], "traction": snapshot["traction"],
            "decision": deepcopy(snapshot["decision"]), "command": deepcopy(snapshot["command"]),
            "tracks": deepcopy(snapshot["tracks"]), "radar_health": health, "communication_health": link,
            "event": {k: v for k, v in snapshot["events"][-1].items() if k != "event_id"},
            "counts": self.counts(), "protocol": deepcopy(snapshot["protocol"]),
            "client": {"session_id": c.session_id, "last_sequence": c.last_sequence, "terminal": list(c.terminal),
                       "pending": {str(k): asdict(v) for k, v in c.pending.items()}, "invalid_feedback": c.invalid_feedback},
            "receiver": {"boot_id": self.endpoint.boot_id, "session_id": self.endpoint.session_id,
                         "local_expiry_ns": self.endpoint.local_expiry_ns, "last_sequence": self.endpoint.last_sequence,
                         "reason": self.endpoint.last_reason, "output_state": self.endpoint.output_state},
            "transport": deepcopy(self.transport_result),
            "recording": None if current_session is None else {k: current_session[k] for k in ("record_count", "status")},
            "replay": deepcopy(self.replay_result), "observer_reads": observers}


def run_scenario(scenario: Scenario, run_id: str = "test") -> dict:
    started = time.perf_counter()
    with isolated_environment() as guard:
        # Import only after the environment guard: main's existing module-level
        # ASGI object must also be constructed with memory storage.
        from app.main import create_app, DeploymentConfig
        from fastapi.testclient import TestClient
        run = ControlledRun(scenario, run_id)
        app = create_app(settings(), DeploymentConfig(), runtime_factory=run.factory)
        with TestClient(app) as client:
            run.trace.append(run.row(0, "START", {}, run.observe(client)))
            for index, step in enumerate(scenario.steps, 1):
                run.act(step, client)
                row = run.row(index, step.action, step.args, run.observe(client))
                assert_expected(scenario.scenario_id, index, step.expect, row["facts"])
                run.trace.append(row)
            if run.trace[-1]["facts"]["state"] != scenario.expected_final_state:
                raise EvidenceFailure("wrong final state")
        if not run.owner.closed or not run.owner.task.done():
            raise EvidenceFailure("runtime shutdown incomplete")
        return {"scenario_id": scenario.scenario_id, "run_id": run_id, "result": "PASS", "seed": SEED,
                "digest": trace_digest(run.trace), "trace": run.trace, "replay": run.portable,
                "hardware_opener_calls": guard.calls, "host_duration_s": round(time.perf_counter()-started, 6),
                "counts": run.trace[-1]["counts"], "shutdown_complete": True}
