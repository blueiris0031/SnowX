from typing import Any
import asyncio


class SafeDBOperateLock:
    def __init__(self, base_lock: Any | None = None) -> None:
        self._db_lock = base_lock or asyncio.Lock()

        self._db_event = asyncio.Event()
        self._db_event.clear()

        self._op_count = 0
        self._op_event = asyncio.Event()
        self._op_event.set()

    async def __aenter__(self) -> None:
        await self._db_event.wait()
        self._op_count += 1
        self._op_event.clear()
        await self._db_lock.__aenter__()

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self._db_lock.__aexit__(*args, **kwargs)
        self._op_count = max(self._op_count - 1, 0)
        if self._op_count == 0:
            self._op_event.set()

    async def set_init(self):
        self._db_event.set()

    async def set_close(self):
        self._db_event.clear()
        await self._op_event.wait()


__all__ = [
    "SafeDBOperateLock"
]
