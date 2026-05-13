import asyncio
from typing import Hashable, Type

from .bus import global_event_bus
from ..config import config_manager
from ..logger import LoggerManager
from ...types.event import BaseEvent
from ...utils.queue import TypedAsyncQueue
from ...utils.worker import ProducerConsumerWorker
from copy import copy


DISTRIBUTOR_QUEUE_MAXSIZE = config_manager.get_config("DISTRIBUTOR_QUEUE_MAXSIZE", 1024)
DISTRIBUTOR_BUFFER_MAXSIZE = config_manager.get_config("DISTRIBUTOR_BUFFER_MAXSIZE", 256)

LOGGER = LoggerManager().get_logger("EventDistributor")


class EventDistributorManager:
    def __init__(self):
        self._distributors: dict[Hashable, tuple[TypedAsyncQueue, set[Type[BaseEvent]]]] = {}

        self._worker = ProducerConsumerWorker(
            self._producer,
            self._consumer,
            DISTRIBUTOR_BUFFER_MAXSIZE,
        )
        LOGGER.debug("ProducerConsumerWorker initialized.")

        self._event_distributor_cache: dict[Type[BaseEvent], list[TypedAsyncQueue]] = {}
        LOGGER.debug("EventDistributorManager initialized.")

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

    def get_distributor(self, symbol: Hashable, event_types: tuple[Type[BaseEvent], ...], replace: bool = False) -> TypedAsyncQueue:
        distributor, rec_types = self._distributors.setdefault(symbol, (TypedAsyncQueue(BaseEvent, DISTRIBUTOR_QUEUE_MAXSIZE), set()))

        old_types = copy(rec_types)
        if replace:
            rec_types.clear()

        rec_types.update(event_types)
        if old_types != rec_types:
            self._event_distributor_cache.clear()

        return distributor

    def del_distributor(self, symbol: Hashable) -> None:
        self._event_distributor_cache.clear()
        self._distributors.pop(symbol, None)

    def clear_distributor(self) -> None:
        self._event_distributor_cache.clear()
        self._distributors.clear()

    async def start(self) -> None:
        if self._worker.is_running():
            LOGGER.warning("Distributor is already running.")
            return

        await self._worker.start()
        LOGGER.info("Distributor started successfully.")

    async def stop(self, force_stop: bool = False) -> None:
        if not self._worker.is_running():
            LOGGER.warning("Distributor is not running.")
            return

        await self._worker.stop(force_stop)
        self.clear_distributor()
        LOGGER.info("Distributor stopped successfully.")


event_distributor_manager = EventDistributorManager()
LOGGER.debug("EventDistributorManager initialized.")


__all__ = [
    "event_distributor_manager",
]
