import asyncio
from typing import Any, Callable, Coroutine

from .lock import AsyncCompletionLock


class ProducerConsumerWorker:
    def __init__(
            self,
            producer_func: Callable[[], Coroutine[None, None, Any | None]],
            consumer_func: Callable[[...], Coroutine[None, None, Any]],
            consumer_queue_maxsize: int = 0,
    ) -> None:
        self._producer_func = producer_func
        self._consumer_func = consumer_func

        self._run_sign: bool = False
        self._completion_lock: AsyncCompletionLock | None = None
        self._producer_loop_task: asyncio.Task | None = None
        self._consumer_queue: asyncio.Queue[asyncio.Task[Any] | None] = asyncio.Queue(consumer_queue_maxsize)
        self._consumer_loop_task: asyncio.Task | None = None

    async def _producer_loop(self) -> None:
        while self._run_sign:
            event = await self._producer_func()
            if event is None:
                continue

            async with self._completion_lock:
                consumer = asyncio.create_task(self._consumer_func(event))
                await self._consumer_queue.put(consumer)

    async def _consumer_loop(self) -> None:
        while True:
            if (not self._run_sign) and self._consumer_queue.empty():
                break

            consumer = await self._consumer_queue.get()
            self._consumer_queue.task_done()

            if consumer is None:
                continue

            await consumer

    async def _clean_consumer(self) -> None:
        while not self._consumer_queue.empty():
            consumer = self._consumer_queue.get_nowait()
            self._consumer_queue.task_done()
            if consumer is None:
                continue

            consumer.cancel()
            try:
                await consumer
            except asyncio.CancelledError:
                pass

    def is_running(self) -> bool:
        return self._run_sign

    async def start(self) -> None:
        if self._run_sign:
            return

        self._run_sign = True
        self._completion_lock = AsyncCompletionLock()
        self._producer_loop_task = asyncio.create_task(self._producer_loop())
        self._consumer_loop_task = asyncio.create_task(self._consumer_loop())

    async def stop(self, force_stop: bool = False) -> None:
        if not self._run_sign:
            return

        self._run_sign = False

        if not force_stop:
            await self._completion_lock.wait()
            await self._consumer_queue.put(None)
        else:
            self._consumer_loop_task.cancel()
        self._producer_loop_task.cancel()

        try:
            await self._producer_loop_task
        except asyncio.CancelledError:
            pass
        self._producer_loop_task = None

        try:
            await self._consumer_loop_task
        except asyncio.CancelledError:
            pass
        self._consumer_loop_task = None

        await self._clean_consumer() # Cleaning up of forced stop.
        self._completion_lock = None


__all__ = [
    "ProducerConsumerWorker",
]
