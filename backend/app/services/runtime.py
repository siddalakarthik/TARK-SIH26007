"""One lifespan-owned decision task; observers only receive detached snapshots."""
from __future__ import annotations

import asyncio
from copy import deepcopy
import time
from typing import Awaitable, Callable

from app.services.system import TarkSystem
from app.r3.evidence import age_readiness


class RuntimeUnavailable(RuntimeError):
    pass


class RuntimeOwner:
    # Preserve the prior 250 ms publication interval as the nominal runtime
    # interval. No catch-up bursts and no observer-dependent execution.
    INTERVAL_S = 0.25

    def __init__(self, system: TarkSystem, *, clock: Callable[[], int] = time.monotonic_ns,
                 wait: Callable[[float], Awaitable[None]] = asyncio.sleep):
        self.system = system
        self.clock = clock
        self.wait = wait
        self.task: asyncio.Task | None = None
        self.closed = False
        self._snapshot: dict | None = None

    async def start(self) -> None:
        if self.task is not None or self.closed:
            raise RuntimeError("runtime owner already started or closed")
        self._advance()
        self.task = asyncio.create_task(self._run(), name="tark-decision-owner")

    def _advance(self) -> None:
        self._snapshot = self.system.tick(self.clock())

    async def _run(self) -> None:
        while True:
            await self.wait(self.INTERVAL_S)
            self._advance()

    def latest(self) -> dict:
        snapshot = self._snapshot
        if self.closed or self.task is None or self.task.done() or snapshot is None:
            raise RuntimeUnavailable("Decision runtime unavailable; no current snapshot")
        now_ns = self.clock()
        age_ns = now_ns - snapshot["timestamp_ns"]
        if not 0 <= age_ns <= self.system.settings.stale_age_ms * 1_000_000:
            raise RuntimeUnavailable("Decision runtime snapshot stale; no current evidence")
        evidence_deadline = snapshot.get("normal_evidence_valid_until_ns")
        if evidence_deadline is not None and now_ns > evidence_deadline:
            raise RuntimeUnavailable("Decision evidence expired; awaiting next runtime snapshot")
        result=deepcopy(snapshot)
        if 'r3' in result:
            result['r3']=age_readiness(result['r3'],now_ns)
        return result

    async def stop(self) -> None:
        self.closed = True
        if self.task is not None:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            # A worker failure is not suppressed: it is unavailable to readers
            # immediately and is propagated at shutdown for operator evidence.
