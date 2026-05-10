from asyncio import BoundedSemaphore, Event, Semaphore
from typing import Literal, overload


class AsyncWaitGroup:
    def __init__(self):
        self._completion_event = Event()
        self._completion_event.set()
        self._enter_count = 0

    async def __aenter__(self):
        self._completion_event.clear()
        self._enter_count += 1

    async def __aexit__(self, *_):
        self._enter_count -= 1
        if self._enter_count == 0:
            self._completion_event.set()

    async def wait(self):
        await self._completion_event.wait()


class _BaseUnlimitedSemaphore:
    def locked(self) -> Literal[False]: return False
    async def acquire(self) -> Literal[True]: return True
    def release(self) -> None: pass
    async def __aenter__(self) -> None: await self.acquire()
    async def __aexit__(self, *_) -> None: self.release()


class _UnlimitedSemaphore(_BaseUnlimitedSemaphore): pass
class _UnlimitedBoundedSemaphore(_BaseUnlimitedSemaphore):
    def __init__(self): self._count = 0
    async def acquire(self):
        self._count += 1
        return super().acquire()

    def release(self):
        if self._count == 0:
            raise ValueError('BoundedSemaphore released too many times')
        self._count -= 1


@overload
def get_semaphore(value: int, bounded: Literal[True] = True) -> BoundedSemaphore: ...
@overload
def get_semaphore(value: int, bounded: Literal[False] = False) -> Semaphore: ...
def get_semaphore(value: int, bounded: Literal[True, False] = True):
    """
    If the value is a number less than 0, return the corresponding UnlimitedSemaphore. \n
    Note: UnlimitedSemaphore interface may differ from the standard implementation.
    """
    if value <= 0:
        if bounded:
            return _UnlimitedBoundedSemaphore()
        return _UnlimitedSemaphore()
    if bounded:
        return BoundedSemaphore(value)
    return Semaphore(value)


__all__ = [
    "AsyncWaitGroup",

    "get_semaphore",
]
