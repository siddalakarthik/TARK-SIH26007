"""Verified HLK-LD2450 target-report decoding.

The binary report below is the manufacturer-published target-data frame: four
header bytes ``AA FF 03 00``, three eight-byte target slots, then ``55 CC``.
It deliberately does *not* implement configuration commands or infer any
undocumented frame type.  ``SIM1`` remains a deterministic test-fixture
format; it is never selected by the physical serial adapter.
"""

from __future__ import annotations

import json
import math

from app.domain.models import RadarDetection


class FrameError(ValueError):
    """A complete candidate frame failed its documented structural checks."""


class LD2450Parser:
    """Incrementally decode bounded, fixed-size LD2450 target reports."""

    HEADER = b"\xAA\xFF\x03\x00"
    FOOTER = b"\x55\xCC"
    TARGET_COUNT = 3
    TARGET_SIZE = 8
    FRAME_SIZE = len(HEADER) + TARGET_COUNT * TARGET_SIZE + len(FOOTER)
    # The published LD2450 operating range is six metres.  A target outside
    # that envelope is rejected rather than passed into the safety pipeline.
    MAX_RANGE_M = 6.0

    def __init__(self, max_buffer_bytes: int | None = None):
        max_buffer_bytes = max_buffer_bytes or self.FRAME_SIZE * 4
        if max_buffer_bytes < self.FRAME_SIZE:
            raise ValueError("max_buffer_bytes must retain one complete frame")
        self._buffer = bytearray()
        self.max_buffer_bytes = max_buffer_bytes
        self.valid_frame_count = 0
        self.rejected_frame_count = 0

    @staticmethod
    def _signed_magnitude(low: int, high: int) -> int:
        """Decode the protocol's little-endian sign/magnitude 16-bit field."""
        raw = low | (high << 8)
        magnitude = raw & 0x7FFF
        return magnitude if raw & 0x8000 else -magnitude

    def _decode_report(self, raw: bytes, arrival_ns: int) -> list[RadarDetection]:
        if len(raw) != self.FRAME_SIZE:
            raise FrameError("INVALID_LD2450_LENGTH")
        if not raw.startswith(self.HEADER):
            raise FrameError("INVALID_LD2450_HEADER")
        if not raw.endswith(self.FOOTER):
            raise FrameError("INVALID_LD2450_FOOTER")

        detections: list[RadarDetection] = []
        for slot in range(self.TARGET_COUNT):
            offset = len(self.HEADER) + slot * self.TARGET_SIZE
            record = raw[offset : offset + self.TARGET_SIZE]
            # An all-zero record is the documented "no target" slot.
            if record == b"\x00" * self.TARGET_SIZE:
                continue
            x_m = self._signed_magnitude(record[0], record[1]) / 1000.0
            y_m = self._signed_magnitude(record[2], record[3]) / 1000.0
            velocity_mps = self._signed_magnitude(record[4], record[5]) / 100.0
            resolution_m = (record[6] | (record[7] << 8)) / 1000.0
            if math.hypot(x_m, y_m) > self.MAX_RANGE_M:
                raise FrameError("IMPOSSIBLE_LD2450_RANGE")
            # The target report has no confidence field.  Do not manufacture
            # one: zero means no vendor-provided confidence, while reported
            # range resolution is retained as the bounded uncertainty input.
            detections.append(
                RadarDetection(
                    source_id="ld2450",
                    candidate_id=slot + 1,
                    x_m=x_m,
                    y_m=y_m,
                    velocity_mps=velocity_mps,
                    quality=0.0,
                    uncertainty_m=max(0.0, resolution_m),
                    timestamp_ns=arrival_ns,
                )
            )
        return detections

    def feed(self, raw: bytes, arrival_ns: int) -> list[list[RadarDetection]]:
        """Accept arbitrary serial chunks and recover from noise/corruption."""
        self._buffer.extend(raw)
        if len(self._buffer) > self.max_buffer_bytes:
            del self._buffer[: len(self._buffer) - self.max_buffer_bytes]
        reports: list[list[RadarDetection]] = []
        while True:
            start = self._buffer.find(self.HEADER)
            if start < 0:
                # Preserve only a possible partial header for the next read.
                keep = len(self.HEADER) - 1
                if len(self._buffer) > keep:
                    del self._buffer[:-keep]
                break
            if start:
                del self._buffer[:start]
            if len(self._buffer) < self.FRAME_SIZE:
                break
            candidate = bytes(self._buffer[: self.FRAME_SIZE])
            try:
                reports.append(self._decode_report(candidate, arrival_ns))
                self.valid_frame_count += 1
                del self._buffer[: self.FRAME_SIZE]
            except FrameError:
                # Shift one byte, then look for the next documented header.
                self.rejected_frame_count += 1
                del self._buffer[:1]
        return reports

    def parse(self, raw: bytes, arrival_ns: int) -> list[RadarDetection]:
        """Decode exactly one report, retaining the established SIM1 fixture."""
        if raw.startswith(b"SIM1 ") and raw.endswith(b"\n"):
            try:
                payload = json.loads(raw[5:-1])
            except json.JSONDecodeError as error:
                raise FrameError("INVALID_SIM1_JSON") from error
            return [
                RadarDetection(
                    candidate_id=int(item["id"]), x_m=float(item["x_m"]),
                    y_m=float(item["y_m"]), velocity_mps=float(item["velocity_mps"]),
                    quality=float(item["quality"]),
                    uncertainty_m=float(item.get("uncertainty_m", 0.5)), timestamp_ns=arrival_ns,
                )
                for item in payload.get("detections", [])
            ]
        # ``parse`` is intentionally a strict one-frame convenience API for
        # replay/tests.  Serial code uses ``feed`` so a rejected test/replay
        # frame cannot leave hidden bytes in the streaming buffer.
        return self._decode_report(raw, arrival_ns)
