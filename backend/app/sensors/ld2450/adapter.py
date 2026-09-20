from __future__ import annotations
import os
import threading
import time
from dataclasses import dataclass
from typing import Callable

from app.domain.models import RadarDetection
from app.sensors.ld2450.parser import LD2450Parser


@dataclass(frozen=True)
class LD2450RawCaptureConfig:
    """Configuration for the documented target-report reader boundary."""
    port: str = ""
    baudrate: int = 256000
    reconnect_s: float = 0.5

    @classmethod
    def from_environment(cls) -> "LD2450RawCaptureConfig":
        def integer(name: str, default: int) -> int:
            try:
                return int(os.getenv(name, str(default)))
            except ValueError:
                return default
        def number(name: str, default: float) -> float:
            try:
                return float(os.getenv(name, str(default)))
            except ValueError:
                return default
        return cls(
            port=os.getenv("TARK_RADAR_PORT", "").strip(),
            baudrate=integer("TARK_RADAR_BAUD", 256000),
            reconnect_s=max(0.1, number("TARK_RADAR_RECONNECT_INTERVAL_S", 0.5)),
        )

class LD2450Adapter:
    """Bounded serial reader; physical pin and voltage claims remain external."""
    def __init__(self, port: str, baudrate: int=256000, raw_sink: Callable[[int, bytes], None] | None=None):
        self.port=port; self.baudrate=baudrate; self.raw_sink=raw_sink; self._serial=None
        self.last_timestamp_ns: int|None=None; self.last_byte_count=0; self.last_error: str|None=None
    def open(self) -> None:
        try:
            import serial
        except ImportError as error: raise RuntimeError("pyserial is required for real_radar mode") from error
        self._serial=serial.Serial(self.port, self.baudrate, timeout=0.2, bytesize=8, parity="N", stopbits=1)
    def read(self) -> tuple[int, bytes]:
        if self._serial is None: raise RuntimeError("adapter is not open")
        # Binary reports are neither newline-delimited nor text.  A bounded
        # read permits partial/multiple frames for the incremental parser.
        timestamp_ns=time.monotonic_ns(); raw=self._serial.read(256)
        self.last_timestamp_ns=timestamp_ns; self.last_byte_count=len(raw)
        if raw and self.raw_sink is not None:
            try: self.raw_sink(timestamp_ns,raw)
            except Exception as error: self.last_error=f"RAW_SINK_{type(error).__name__}"
        return timestamp_ns, raw
    def close(self) -> None:
        if self._serial is not None: self._serial.close(); self._serial=None
    def diagnostics(self) -> dict:
        return {"state":"NOT_CONNECTED","protocol":"HLK_LD2450_TARGET_REPORT_V1_03","last_timestamp_ns":self.last_timestamp_ns,"last_byte_count":self.last_byte_count,"last_error":self.last_error}


class LD2450RawCaptureWorker:
    """One bounded serial reader with raw evidence, decoder and reconnects."""
    def __init__(
        self,
        adapter: LD2450Adapter,
        reconnect_s: float = 0.5,
        parser: LD2450Parser | None = None,
        on_report: Callable[[int, list[RadarDetection]], None] | None = None,
    ):
        self.adapter = adapter
        self.reconnect_s = max(0.1, reconnect_s)
        self.parser = parser or LD2450Parser()
        self.on_report = on_report
        self.state = "NOT_CONNECTED"
        self.reason = "LD2450 READER NOT STARTED"
        self.reconnect_count = 0
        self.read_count = 0
        self.decoded_report_count = 0
        self.callback_error_count = 0
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> bool:
        if self.running:
            return False
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="tark-ld2450-raw", daemon=True)
        self._thread.start()
        return True

    def close(self) -> None:
        self._stop.set()
        self.adapter.close()
        if self._thread:
            self._thread.join(timeout=2)
        self._thread = None
        self.state = "NOT_CONNECTED"
        self.reason = "LD2450 READER STOPPED"

    def diagnostics(self) -> dict:
        return {
            **self.adapter.diagnostics(),
            "state": self.state,
            "reason": self.reason,
            "reconnect_count": self.reconnect_count,
            "read_count": self.read_count,
            "decoded_report_count": self.decoded_report_count,
            "rejected_frame_count": self.parser.rejected_frame_count,
            "callback_error_count": self.callback_error_count,
        }

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self.state = "OPENING"
                self.reason = "OPENING CONFIGURED LD2450 PORT"
                self.adapter.open()
                self.state = "ONLINE"
                self.reason = "VERIFIED LD2450 TARGET-REPORT DECODER ACTIVE"
                while not self._stop.is_set():
                    timestamp_ns, raw = self.adapter.read()
                    self.read_count += 1
                    for detections in self.parser.feed(raw, timestamp_ns):
                        self.decoded_report_count += 1
                        if self.on_report is not None:
                            try:
                                self.on_report(timestamp_ns, detections)
                            except Exception:
                                # Callback faults must not stop raw retention
                                # or force a transport fault into authority.
                                self.callback_error_count += 1
            except Exception as error:
                self.state = "ERROR"
                self.reason = f"LD2450 READER ERROR: {type(error).__name__}"
                self.reconnect_count += 1
            finally:
                self.adapter.close()
            if not self._stop.wait(self.reconnect_s):
                continue
