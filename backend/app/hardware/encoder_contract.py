"""Hardware-neutral wheel-response counter contract.

No encoder electrical or mechanical characteristic is assumed here.  In
particular, counts are not converted into ground speed or distance: that needs
the verified purchased encoder's resolution, polarity and wheel geometry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


EncoderState = Literal["NOT_CONNECTED", "NO_DATA", "ONLINE", "STALE", "INVALID", "FAULT", "SIMULATION"]
EncoderSource = Literal["SIMULATION", "REAL", "NOT_CONNECTED", "FAULT"]


@dataclass(frozen=True)
class EncoderCounts:
    left_count: int | None
    right_count: int | None
    timestamp_ns: int | None
    source_mode: EncoderSource
    state: EncoderState
    reason: str
    left_delta: int | None = None
    right_delta: int | None = None


class EncoderContract:
    """Validate timestamped count observations and optional known counter wrap.

    ``counter_modulus`` and ``max_count_delta`` are deliberately opt-in.  They
    cannot be selected until the exact encoder/ESP32 counter representation is
    verified, so defaults report counts but never invent a physical limit.
    """

    def __init__(self, counter_modulus: int | None = None, max_count_delta: int | None = None):
        if counter_modulus is not None and counter_modulus < 2:
            raise ValueError("counter_modulus must be at least two")
        if max_count_delta is not None and max_count_delta < 0:
            raise ValueError("max_count_delta must be non-negative")
        self.counter_modulus = counter_modulus
        self.max_count_delta = max_count_delta
        self.last: EncoderCounts | None = None

    def _delta(self, current: int, previous: int) -> int:
        delta = current - previous
        if self.counter_modulus is not None:
            half = self.counter_modulus // 2
            if delta > half:
                delta -= self.counter_modulus
            elif delta < -half:
                delta += self.counter_modulus
        return delta

    def accept(self, left_count: int, right_count: int, timestamp_ns: int, source_mode: EncoderSource) -> EncoderCounts:
        if source_mode not in {"SIMULATION", "REAL"}:
            return EncoderCounts(None, None, None, source_mode, "NOT_CONNECTED" if source_mode == "NOT_CONNECTED" else "FAULT", "ENCODER_SOURCE_UNAVAILABLE")
        if any(isinstance(value, bool) or not isinstance(value, int) for value in (left_count, right_count, timestamp_ns)) or timestamp_ns < 0:
            return EncoderCounts(None, None, None, source_mode, "INVALID", "INVALID_ENCODER_COUNT_OR_TIMESTAMP")
        if self.counter_modulus is not None and (not 0 <= left_count < self.counter_modulus or not 0 <= right_count < self.counter_modulus):
            return EncoderCounts(None, None, None, source_mode, "INVALID", "ENCODER_COUNT_OUTSIDE_CONFIGURED_MODULUS")
        previous = self.last
        if previous is not None and previous.timestamp_ns is not None:
            if timestamp_ns <= previous.timestamp_ns:
                return EncoderCounts(left_count, right_count, timestamp_ns, source_mode, "INVALID", "NON_MONOTONIC_ENCODER_TIMESTAMP")
            left_delta = self._delta(left_count, previous.left_count or 0)
            right_delta = self._delta(right_count, previous.right_count or 0)
            if self.max_count_delta is not None and (abs(left_delta) > self.max_count_delta or abs(right_delta) > self.max_count_delta):
                return EncoderCounts(left_count, right_count, timestamp_ns, source_mode, "INVALID", "IMPOSSIBLE_ENCODER_COUNT_JUMP", left_delta, right_delta)
        else:
            left_delta = right_delta = 0
        state: EncoderState = "SIMULATION" if source_mode == "SIMULATION" else "ONLINE"
        result = EncoderCounts(left_count, right_count, timestamp_ns, source_mode, state, "WHEEL_RESPONSE_COUNTS_ONLY", left_delta, right_delta)
        self.last = result
        return result

    def health(self, now_ns: int, freshness_ns: int) -> EncoderCounts:
        if self.last is None:
            return EncoderCounts(None, None, None, "NOT_CONNECTED", "NO_DATA", "NO_ENCODER_OBSERVATION")
        if now_ns < self.last.timestamp_ns or now_ns - self.last.timestamp_ns > freshness_ns:
            return EncoderCounts(self.last.left_count, self.last.right_count, self.last.timestamp_ns, self.last.source_mode, "STALE", "ENCODER_OBSERVATION_STALE", self.last.left_delta, self.last.right_delta)
        return self.last
