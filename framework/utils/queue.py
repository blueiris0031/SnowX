import asyncio
from typing import Any, Type


class TypedAsyncQueue(asyncio.Queue):
    def __init__(self, allowed_type: Type[Any], maxsize: int = 0):
        self._allowed_type = allowed_type
        super().__init__(maxsize)

    async def bulk_put(self, items: tuple[Any, ...]) -> None:
        for item in items:
            if not isinstance(item, self._allowed_type):
                continue

            await self.put(item)

    async def auto_put(self, item: tuple[Any, ...] | Any | None) -> None:
        if isinstance(item, tuple):
            await self.bulk_put(item)
            return

        if isinstance(item, self._allowed_type):
            await self.put(item)


__all__ = [
    "TypedAsyncQueue",
]
