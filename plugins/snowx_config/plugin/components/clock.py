import asyncio
from typing import Any, Callable, Hashable, Iterable

from snowx.api.logger import get_logger
from snowx.utils.worker import ProducerConsumerWorker


class ClockWorker:
    _logger = get_logger("SnowXConfig.ClockWorker")

    def __init__(self, interval: int = 1):
        self._interval = interval

        self._worker = ProducerConsumerWorker(
            self._producer,
            self._consumer,
        )
        self._task: dict[Hashable, tuple[Callable[..., None], Iterable[Any], dict[str, Any]]] = {}

    def submit_task(
            self,
            symbol: Hashable,
            func: Callable[..., Any],
            args: Iterable[Any],
            kwargs: dict[str, Any],
            cover: bool = True,
    ) -> None:
        if symbol in self._task and not cover:
            return

        self._task[symbol] = (func, args, kwargs)

    async def _producer(self) -> int:
        await asyncio.sleep(self._interval)
        return 1

    async def _consumer(self, _) -> None:
        for _, task in self._task.items():
            func, args, kwargs = task
            try:
                func(*args or (), **kwargs or {})
            except Exception as e:
                self._logger.error(f"Task exception", exc_info=e)

        self._task.clear()

    async def start(self) -> None:
        if self._worker.is_running():
            self._logger.warning("Worker is already running.")
            return

        await self._worker.start()
        self._logger.info("Worker started successfully.")

    async def stop(self, force_stop: bool = False) -> None:
        if not self._worker.is_running():
            self._logger.warning("Worker is not running.")
            return

        await self._worker.stop(force_stop)
        self._logger.info("Worker stopped successfully.")


clock_worker = ClockWorker()


__all__ = [
    "clock_worker",
]
