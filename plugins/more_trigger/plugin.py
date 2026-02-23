import asyncio
import time
from datetime import datetime

from croniter import croniter
from snowx.base.trigger import BaseTrigger


class IntervalTrigger(BaseTrigger):
    def __init__(self, interval: int | float):
        self._interval = interval

    async def wait(self) -> None:
        await asyncio.sleep(self._interval)


class ControllableTrigger(BaseTrigger):
    def __init__(self):
        self._event = asyncio.Event()

    async def wait(self) -> None:
        await self._event.wait()
        await asyncio.sleep(0)

    def enable(self) -> None:
        self._event.set()

    def disable(self) -> None:
        self._event.clear()


class ResetTrigger(BaseTrigger):
    def __init__(self):
        self._event = asyncio.Event()

    async def wait(self) -> None:
        await self._event.wait()
        self._event.clear()

    def enable(self) -> None:
        self._event.set()


class CronTrigger(BaseTrigger):
    def __init__(self, expr_format: str):
        self.expr_format = expr_format
        self.start_time = datetime.now()
        self.croniter = croniter(self.expr_format, self.start_time, ret_type=datetime)

    def test_expr(self):
        print(self.croniter.get_next())

    async def wait(self):
        await asyncio.sleep(max(0, self.croniter.get_next().timestamp() - time.time()))


__all__ = [
    "IntervalTrigger",
    "ControllableTrigger",
    "ResetTrigger",
    "CronTrigger",
]
