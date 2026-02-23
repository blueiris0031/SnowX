import asyncio
import logging
from collections.abc import Awaitable
from types import MappingProxyType
from typing import Any, Callable, Type

from .container import CallbackContainer
from ...base.callback import BaseSchedulerItem
from ...constants.callback import EXECUTION_METHOD
from ...kernel.logger import get_logger
from ...types.callback import CallbackItem, CallbackResultItem


LOGGER = get_logger("SchedulerManager")


class SchedulerManager:
    """
    Scheduler Instance Manager.
    """
    def __init__(
            self,
            cb_type: str,
            container: CallbackContainer,
            scheduler_item: Type[BaseSchedulerItem],
            scheduler_kwargs: dict[str, Any] | None = None,
            **inject_functions: Callable[["SchedulerManager", ...], Any],
    ):
        """
        :param cb_type: Callback type
        :param container: Callback container
        :param scheduler_item: Type of scheduler item
        :param scheduler_kwargs: Scheduler default kwargs
        :param inject_functions: Inject the function of the manager.
         The first parameter of this function is the manager instance.
        """
        self._cb_type = cb_type
        self._container = container
        self._scheduler_item = scheduler_item
        self._scheduler_kwargs = scheduler_kwargs or {}
        self._schedulers: dict[str, BaseSchedulerItem] = {}
        if inject_functions:
            self._inject(inject_functions)

    @property
    def logger(self) -> logging.Logger:
        return LOGGER

    @property
    def cb_type(self) -> str:
        return self._cb_type

    @property
    def container(self) -> CallbackContainer:
        return self._container

    @property
    def scheduler_item(self) -> Type[BaseSchedulerItem]:
        return self._scheduler_item

    @property
    def scheduler_kwargs(self) -> MappingProxyType[str, Any]:
        return MappingProxyType(self._scheduler_kwargs)

    @property
    def schedulers(self) -> MappingProxyType[str, BaseSchedulerItem]:
        return MappingProxyType(self._schedulers)

    def _wrap_func(self, func: Callable[["SchedulerManager", ...], Any]) -> Callable[..., Any]:
        def wrapped_func(*args, **kwargs) -> Any:
            return func(self, *args, **kwargs)

        return wrapped_func

    def _inject(self, inject_functions: dict[str, Callable[["SchedulerManager", ...], Any]]):
        for key, func in inject_functions.items():
            if not hasattr(self, key):
                setattr(self, key, self._wrap_func(func))

    async def start(self, identifier: str, **item_kwargs) -> None:
        """
        Start a scheduler instance according to the identifier.
        :param identifier: Identifier of the scheduler instance
        :param item_kwargs: Overwrite or extend the parameters of the scheduler.
         If this parameter is empty, the default scheduler parameter will be used.
        :return: None
        """
        if identifier in self._schedulers:
            self.logger.info(f"[<{self.cb_type}>scheduler]:<{identifier}> is already running.")
            return

        callbacks = self.container.get(self.cb_type, identifier)
        if not callbacks:
            self.logger.info(f"[<{self.cb_type}>scheduler]:<{identifier}> no registered callback found, skip startup.")
            return

        new_scheduler = self._scheduler_item(
            self.cb_type,
            identifier,
            *callbacks,
            **{**self.scheduler_kwargs, **item_kwargs},
        )
        self._schedulers[identifier] = new_scheduler
        await new_scheduler.start()
        self.logger.info(f"[<{self.cb_type}>scheduler]:<{identifier}> started successfully.")

    async def stop(self, identifier: str, force_stop: bool = False) -> None:
        """
        Stop a scheduler instance according to the identifier.
        :param identifier: If there is a scheduler with the corresponding identifier in the manager, it will be stopped.
        :param force_stop: If this parameter is true, the scheduler will be forcibly stopped.
        :return: None
        """
        if identifier not in self._schedulers:
            self.logger.info(f"[<{self.cb_type}>scheduler]:<{identifier}> is not running.")
            return

        scheduler = self._schedulers[identifier]
        await scheduler.stop(force_stop)
        self.logger.info(f"[<{self.cb_type}>scheduler]:<{identifier}> stopped successfully.")
        del self._schedulers[identifier]


class SingleExecutionSchedulerItem(BaseSchedulerItem):
    """
    Note: The callback function of this scheduler must be wrapped by the executor, otherwise the results cannot be obtained correctly. \n
    For detailed information about the executor, please refer to [Components-Callback-Executor] chapter of the development document.
    """
    def __init__(
            self,
            cb_type: str,
            identifier: str,
            *callbacks: tuple[CallbackItem, ...],
            execution_method: Callable[..., Awaitable[tuple[Any, ...]]] = EXECUTION_METHOD.PARALLEL,
    ) -> None:
        super().__init__(cb_type, identifier, *callbacks)

        self._execution_method = execution_method
        self._task: asyncio.Task[tuple[CallbackResultItem, ...]] | None = None

    async def _executor(self) -> tuple[CallbackResultItem, ...]:
        results: list[CallbackResultItem] = []

        cb_results = await self._execution_method(
            *(
                callback.actual_func()
                for callback in self.callbacks
            ),
            return_exceptions=True,
        )
        for callback, result in zip(self.callbacks, cb_results):
            if isinstance(result, tuple):

                results.append(CallbackResultItem(callback, True, *result))
            else:
                results.append(CallbackResultItem(callback, True, False, result))

        return tuple(results)

    async def start(self) -> None:
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._executor())

    async def stop(self, force_stop: bool = False) -> tuple[CallbackResultItem, ...] | None:
        if self._task is None:
            return None

        if force_stop:
            self._task.cancel()

        try:
            result = await self._task
        except asyncio.CancelledError:
            result = None
        self._task = None
        return result

    async def get_result(self) -> tuple[CallbackResultItem, ...]:
        return await self.stop(force_stop=False) or ()


async def get_result(self: SchedulerManager, identifier: str) -> tuple[CallbackResultItem, ...]:
    """
    This function can be injected into the manager who uses the SingleExecutionSchedulerItem.
    """
    if identifier not in self.schedulers:
        return ()

    scheduler = self.schedulers[identifier]
    result = await scheduler.get_result()
    self.logger.info(f"[<{self.cb_type}>scheduler]: <{identifier}> executed successfully.")
    await self.stop(identifier)
    return tuple(result)


__all__ = [
    "SchedulerManager",
    "SingleExecutionSchedulerItem",
    "get_result",
]
