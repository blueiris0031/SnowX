from typing import Hashable

from ..utils.lock import AsyncCompletionLock


class AsyncCompletionLockManager:
    def __init__(self):
        self.locks: dict[Hashable, AsyncCompletionLock] = {}
        self.nowait: set[Hashable] = set()

    def get_lock(self, symbol: Hashable, force_new_lock: bool = False) -> AsyncCompletionLock:
        if not force_new_lock:
            return self.locks.setdefault(symbol, AsyncCompletionLock())

        new_lock = AsyncCompletionLock()
        self.locks[symbol] = new_lock
        return new_lock

    def set_nowait(self, symbol: Hashable) -> None:
        self.nowait.add(symbol)

    def reset_nowait(self, symbol: Hashable) -> None:
        if symbol not in self.nowait:
            return

        self.nowait.remove(symbol)

    async def wait(self, symbol: Hashable) -> None:
        if symbol in self.nowait:
            return

        if symbol not in self.locks:
            return

        await self.locks[symbol].wait()


__all__ = [
    "AsyncCompletionLockManager",
]
