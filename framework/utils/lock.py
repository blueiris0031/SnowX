import asyncio


class AsyncCompletionLock:
    def __init__(self):
        self._runner_lock = asyncio.Event()
        self._runner_lock.set()

        self._enter_count = 0

    async def __aenter__(self):
        self._runner_lock.clear()
        self._enter_count += 1

    async def __aexit__(self, *_):
        self._enter_count = max(0, self._enter_count - 1)
        if self._enter_count == 0:
            self._runner_lock.set()

    async def wait(self):
        await self._runner_lock.wait()


__all__ = [
    "AsyncCompletionLock",
]
