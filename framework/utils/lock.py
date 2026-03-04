import asyncio


class AsyncCompletionLock:
    def __init__(self):
        self._event = asyncio.Event()
        self._event.set()

        self._enter_count = 0

    async def __aenter__(self):
        self._event.clear()
        self._enter_count += 1

    async def __aexit__(self, *_):
        self._enter_count = max(0, self._enter_count - 1)
        if self._enter_count == 0:
            self._event.set()

    async def wait(self):
        await self._event.wait()


__all__ = [
    "AsyncCompletionLock",
]
