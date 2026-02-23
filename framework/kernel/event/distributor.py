import asyncio
from typing import Hashable, Type

from .bus import global_event_bus
from ..config import get_config
from ..logger import get_logger
from ...types.event import BaseEvent
from ...utils.queue import TypedAsyncQueue
from ...utils.worker import ProducerConsumerWorker


DISTRIBUTOR_QUEUE_MAXSIZE = get_config("DISTRIBUTOR_QUEUE_MAXSIZE", 1024)
DISTRIBUTOR_BUFFER_MAXSIZE = get_config("DISTRIBUTOR_BUFFER_MAXSIZE", 256)

LOGGER = get_logger("EventDistributor")


class EventDistributorManager:
    def __init__(self):
        self._distributors: dict[Hashable, tuple[TypedAsyncQueue, set[Type[BaseEvent]]]] = {}

        self._scheduler = ProducerConsumerWorker(
            self._producer,
            self._consumer,
            DISTRIBUTOR_BUFFER_MAXSIZE,
        )

        self._event_distributor_cache: dict[Type[BaseEvent], list[TypedAsyncQueue]] = {}

    def _get_event_distributor(self, event: BaseEvent) -> list[TypedAsyncQueue]:
        event_type = event.__class__
        if event_type in self._event_distributor_cache:
            return self._event_distributor_cache[event_type]

        cache = []
        for distributor in self._distributors.values():
            if any(issubclass(event_type, rec_type) for rec_type in distributor[1]):
                cache.append(distributor[0])

        self._event_distributor_cache[event_type] = cache
        return cache

    @staticmethod
    async def _producer() -> BaseEvent:
        event = await global_event_bus.get()
        global_event_bus.task_done()
        return event

    async def _consumer(self, event: BaseEvent) -> None:
        distributors = self._get_event_distributor(event)
        if not distributors:
            return
        await asyncio.gather(*(queue.auto_put(event) for queue in distributors))

    def get_distributor(self, symbol: Hashable, event_types: set[Type[BaseEvent]]) -> TypedAsyncQueue:
        self._event_distributor_cache.clear()
        return self._distributors.setdefault(symbol, (TypedAsyncQueue(BaseEvent, DISTRIBUTOR_QUEUE_MAXSIZE), event_types))[0]

    def del_distributor(self, symbol: Hashable) -> None:
        self._event_distributor_cache.clear()
        self._distributors.pop(symbol, None)

    def clear_distributor(self) -> None:
        self._event_distributor_cache.clear()
        self._distributors.clear()

    async def start(self) -> None:
        if self._scheduler.is_running():
            LOGGER.warning("Distributor is already running.")
            return

        await self._scheduler.start()
        LOGGER.info("Distributor started successfully.")

    async def stop(self, force_stop: bool = False) -> None:
        if not self._scheduler.is_running():
            LOGGER.warning("Distributor is not running.")
            return

        await self._scheduler.stop(force_stop)
        self.clear_distributor()
        LOGGER.info("Distributor stopped successfully.")


event_distributor_manager = EventDistributorManager()


__all__ = [
    "event_distributor_manager",
]
