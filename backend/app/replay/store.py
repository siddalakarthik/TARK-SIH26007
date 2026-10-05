"""Bounded, local recording storage for observation-only replay.

The store intentionally records what the software received or calculated.  It
never creates a recording on behalf of an unavailable device and it never
replays through an ESP32 transport.
"""
from __future__ import annotations

import base64
import json
import sqlite3
import uuid
from pathlib import Path
from threading import RLock
from typing import Any


class RecordingError(RuntimeError):
    """Raised for an invalid recording operation or recording payload."""


class RecordingStore:
    """One active, bounded recording session per local TARK process."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self._lock = RLock()
        self._active_session_id: str | None = None
        with self._lock:
            self.db.execute(
                """CREATE TABLE IF NOT EXISTS recording_sessions (
                    id TEXT PRIMARY KEY, started_ns INTEGER NOT NULL,
                    stopped_ns INTEGER, source_mode TEXT NOT NULL,
                    configuration_hash TEXT NOT NULL, status TEXT NOT NULL,
                    max_records INTEGER NOT NULL, record_count INTEGER NOT NULL DEFAULT 0
                )"""
            )
            self.db.execute(
                """CREATE TABLE IF NOT EXISTS recording_records (
                    session_id TEXT NOT NULL, sequence INTEGER NOT NULL,
                    timestamp_ns INTEGER NOT NULL, source_mode TEXT NOT NULL,
                    kind TEXT NOT NULL, payload TEXT NOT NULL,
                    PRIMARY KEY (session_id, sequence),
                    FOREIGN KEY(session_id) REFERENCES recording_sessions(id)
                )"""
            )
            columns = {row[1] for row in self.db.execute("PRAGMA table_info(recording_sessions)")}
            if "metadata" not in columns:
                self.db.execute("ALTER TABLE recording_sessions ADD COLUMN metadata TEXT")
            # An abruptly stopped process cannot truthfully resume recording
            # without an explicit operator action. Keep its retained evidence,
            # but mark the boundary as interrupted.
            self.db.execute("UPDATE recording_sessions SET status='INTERRUPTED' WHERE status='RECORDING'")
            self.db.commit()

    @property
    def active_session_id(self) -> str | None:
        return self._active_session_id

    def start(self, *, timestamp_ns: int, source_mode: str, configuration_hash: str, max_records: int, metadata: dict | None = None) -> dict[str, Any]:
        if not 1 <= max_records <= 50_000:
            raise RecordingError("recording max_records must be 1..50000")
        with self._lock:
            if self._active_session_id is not None:
                raise RecordingError("a recording session is already active")
            session_id = str(uuid.uuid4())
            self.db.execute(
                "INSERT INTO recording_sessions VALUES (?,?,?,?,?,?,?,?,?)",
                (session_id, timestamp_ns, None, source_mode, configuration_hash, "RECORDING", max_records, 0, json.dumps(metadata, allow_nan=False) if metadata is not None else None),
            )
            self.db.commit()
            self._active_session_id = session_id
            return self.get(session_id)

    def stop(self, *, timestamp_ns: int) -> dict[str, Any]:
        with self._lock:
            if self._active_session_id is None:
                raise RecordingError("no recording session is active")
            session_id = self._active_session_id
            self.db.execute(
                "UPDATE recording_sessions SET stopped_ns=?, status='COMPLETE' WHERE id=?",
                (timestamp_ns, session_id),
            )
            self.db.commit()
            self._active_session_id = None
            return self.get(session_id)

    def append_observation_tick(self, *, timestamp_ns: int, source_mode: str, payload: dict[str, Any]) -> bool:
        """Append an already-normalized observation tick to the active session.

        Returning False means recording is inactive or the bounded session has
        already completed; no observation is fabricated or silently replaced.
        """
        kind = "OBSERVATION_TICK_V2" if payload.get("schema_version") == 2 else "OBSERVATION_TICK_V1"
        return self._append(timestamp_ns, source_mode, kind, payload)

    def append_raw_frame(self, *, timestamp_ns: int, source_mode: str, raw: bytes, metadata: dict[str, Any] | None = None) -> bool:
        """Retain raw bytes for later vendor-protocol review without decoding them."""
        payload = {
            "schema_version": 1,
            "encoding": "base64",
            "raw": base64.b64encode(raw).decode("ascii"),
            "metadata": metadata or {},
        }
        return self._append(timestamp_ns, source_mode, "RAW_FRAME_V1", payload)

    def _append(self, timestamp_ns: int, source_mode: str, kind: str, payload: dict[str, Any]) -> bool:
        with self._lock:
            session_id = self._active_session_id
            if session_id is None:
                return False
            row = self.db.execute(
                "SELECT max_records, record_count FROM recording_sessions WHERE id=?", (session_id,)
            ).fetchone()
            if row is None:
                self._active_session_id = None
                raise RecordingError("active recording session is missing")
            max_records, record_count = int(row[0]), int(row[1])
            if record_count >= max_records:
                self.db.execute(
                    "UPDATE recording_sessions SET stopped_ns=?, status='FULL' WHERE id=?",
                    (timestamp_ns, session_id),
                )
                self.db.commit()
                self._active_session_id = None
                return False
            self.db.execute(
                "INSERT INTO recording_records VALUES (?,?,?,?,?,?)",
                (session_id, record_count + 1, timestamp_ns, source_mode, kind, json.dumps(payload, sort_keys=True, allow_nan=False)),
            )
            self.db.execute(
                "UPDATE recording_sessions SET record_count=record_count+1 WHERE id=?", (session_id,)
            )
            self.db.commit()
            return True

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = self.db.execute(
                "SELECT id,started_ns,stopped_ns,source_mode,configuration_hash,status,max_records,record_count,metadata "
                "FROM recording_sessions ORDER BY started_ns DESC"
            ).fetchall()
        return [self._session_dict(row) for row in rows]

    def get(self, session_id: str) -> dict[str, Any]:
        with self._lock:
            row = self.db.execute(
                "SELECT id,started_ns,stopped_ns,source_mode,configuration_hash,status,max_records,record_count,metadata "
                "FROM recording_sessions WHERE id=?", (session_id,)
            ).fetchone()
        if row is None:
            raise RecordingError("recording session was not found")
        return self._session_dict(row)

    def records(self, session_id: str, *, limit: int = 1_000, after_sequence: int = 0) -> list[dict[str, Any]]:
        if not 1 <= limit <= 10_000:
            raise RecordingError("record query limit must be 1..10000")
        if type(after_sequence) is not int or after_sequence < 0:
            raise RecordingError("invalid recording cursor")
        self.get(session_id)
        with self._lock:
            rows = self.db.execute(
                "SELECT sequence,timestamp_ns,source_mode,kind,payload FROM recording_records "
                "WHERE session_id=? AND sequence>? ORDER BY sequence ASC LIMIT ?", (session_id, after_sequence, limit)
            ).fetchall()
        result = []
        for sequence, timestamp_ns, source_mode, kind, payload_text in rows:
            try:
                payload = json.loads(payload_text)
            except json.JSONDecodeError as error:
                raise RecordingError("recording contains corrupted JSON payload") from error
            if not isinstance(payload, dict):
                raise RecordingError("recording payload must be an object")
            result.append({"sequence": sequence, "timestamp_ns": timestamp_ns, "source_mode": source_mode, "kind": kind, "payload": payload})
        return result

    def iter_records(self, session_id: str):
        """Keyset pagination: verification does not truncate at a UI page limit."""
        cursor = 0
        while True:
            page = self.records(session_id, limit=256, after_sequence=cursor)
            if not page:
                return
            yield from page
            cursor = page[-1]["sequence"]

    @staticmethod
    def _session_dict(row: tuple[Any, ...]) -> dict[str, Any]:
        try:
            metadata = json.loads(row[8]) if row[8] is not None else None
        except (json.JSONDecodeError, TypeError) as error:
            raise RecordingError("recording contains corrupted metadata") from error
        if metadata is not None and not isinstance(metadata, dict):
            raise RecordingError("recording metadata must be an object")
        return {
            "session_id": row[0], "started_ns": row[1], "stopped_ns": row[2],
            "source_mode": row[3], "configuration_hash": row[4], "status": row[5],
            "max_records": row[6], "record_count": row[7],
            "metadata": metadata,
            "format_status": "VERSIONED" if metadata else "LEGACY_NONDETERMINISTIC",
        }

    def close(self) -> None:
        with self._lock:
            self.db.close()
