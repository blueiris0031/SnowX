import asyncio
import logging

from ..container import CallbackContainer
from ....base.callback import BaseSchedulerItem, get_scheduler_item_cls
from ....utils.void import VoidClass


class SchedulerManager:
    def __init__(
            self,
            container: CallbackContainer,
            logger: logging.Logger | None = None,
    ):
        self._container = container
        self._logger = logger or VoidClass()

        self._scheduler_map: dict[str, dict[str, BaseSchedulerItem]] = {}
        self._scheduler_map_lock = asyncio.Lock()

    @property
    def container(self) -> CallbackContainer:
        return self._container

    @property
    def logger(self) -> logging.Logger | VoidClass:
        return self._logger

    def get_running_item(
            self,
            callback_type: str,
            identifier: str,
    ) -> BaseSchedulerItem | None:
        return self._scheduler_map.get(callback_type, {}).get(identifier, None)

    async def _start(
            self,
            callback_type: str,
            identifier: str,
            *init_args,
            **init_kwargs,
    ) -> None:
        type_map = self._scheduler_map.setdefault(callback_type, {})
        if identifier in type_map:
            self.logger.info(f"[Scheduler<{callback_type}>]: <{identifier}> is already running, skip startup.")
            return

        callbacks = self.container.auto_get(callback_type, identifier)
        if not callbacks:
            self.logger.info(f"[Scheduler<{callback_type}>]: <{identifier}> no registered callback found, skip startup.")
            return

        item_cls = get_scheduler_item_cls(callback_type)
        item_instance = item_cls(callbacks=callbacks, *init_args, **init_kwargs)
        async with self._scheduler_map_lock:
            await item_instance.start()
            type_map[identifier] = item_instance

        self.logger.info(f"[Scheduler<{callback_type}>]: <{identifier}> started successfully.]")

    async def _stop(
            self,
            callback_type: str,
            identifier: str,
            force_stop: bool = False,
    ) -> None:
        if callback_type not in self._scheduler_map:
            self.logger.info(f"[Scheduler<{callback_type}>]: <{identifier}> is not running.")
            return

        type_map = self._scheduler_map[callback_type]
        if identifier not in type_map:
            self.logger.info(f"[Scheduler<{callback_type}>]: <{identifier}> is not running.")
            return

        item_instance = type_map[identifier]
        async with self._scheduler_map_lock:
            await item_instance.stop(force_stop)
            type_map.pop(identifier)

        self.logger.info(f"[Scheduler<{callback_type}>]: <{identifier}> stopped successfully.]")

    def _get_identifier_list(
            self,
            callback_type: str,
            identifier: str | None,
    ) -> tuple[str, ...]:
        return tuple(
            {
                callback.identifier
                for callback in self.container.auto_get(callback_type, identifier)
            }
        )

    async def start(
            self,
            callback_type: str,
            identifier: str | None = None,
            *init_args,
            **init_kwargs,
    ) -> None:
        for id_ in self._get_identifier_list(callback_type, identifier):
            await self._start(callback_type, id_, *init_args, **init_kwargs)

    async def stop(
            self,
            callback_type: str,
            identifier: str | None = None,
            force_stop: bool = False,
    ) -> None:
        for id_ in self._get_identifier_list(callback_type, identifier):
            await self._stop(callback_type, id_, force_stop)


__all__ = [
    "SchedulerManager",
]
