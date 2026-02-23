import asyncio

from ..base.trigger import BaseTrigger


class EmptyTrigger(BaseTrigger):
    async def wait(self) -> None:
        await asyncio.sleep(0)


__all__ = [
    "EmptyTrigger"
]
