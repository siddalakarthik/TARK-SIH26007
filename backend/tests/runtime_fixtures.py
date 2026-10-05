"""Deterministic scheduler driver; never sleeps or touches a physical device."""
import asyncio
from app.services.runtime import RuntimeOwner


class ControlledRuntime:
    def __init__(self):
        self.now = 1_000_000_000
        self.owner = None
        self.queue = None

    def __call__(self, system):
        self.queue = asyncio.Queue()
        self.owner = RuntimeOwner(system, clock=lambda: self.now, wait=self.wait)
        return self.owner

    async def wait(self, delay):
        assert delay == RuntimeOwner.INTERVAL_S
        self.now = await self.queue.get()

    async def step(self, delta_ns=250_000_000):
        before = self.owner.system.pipeline.sequence
        await self.queue.put(self.now + delta_ns)
        for _ in range(100):
            await asyncio.sleep(0)
            if self.owner.system.pipeline.sequence == before + 1:
                return self.owner.latest()
        raise AssertionError('controlled runtime did not consume exactly one step')
