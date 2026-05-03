from typing import Any
import asyncio
from snowx.utils.lock import AsyncCompletionLock


class SafeDBOperateLock(AsyncCompletionLock):
    def __init__(self, base_lock: Any | None = None):
        self._db_lock = base_lock or asyncio.Lock()

        self._db_event = asyncio.Event()
        self._db_event.clear()

        super().__init__()

    async def __aenter__(self) -> None:
        await self._db_event.wait()
        await super().__aenter__()
        await self._db_lock.__aenter__()

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self._db_lock.__aexit__(*args, **kwargs)
        await super().__aexit__()

    async def set_init(self):
        self._db_event.set()

    async def set_close(self):
        self._db_event.clear()
        await super().wait()


__all__ = [
    "SafeDBOperateLock"
]
