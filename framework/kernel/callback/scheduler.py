import asyncio
from typing import Awaitable, Callable, Type

from .container import global_callback_container
from ..config import get_config
from ..event.distributor import event_distributor_manager
from ..lock import global_async_completion_lock_manager
from ..logger import get_logger
from ...base.callback import BaseSchedulerItem
from ...components.callback.scheduler import SchedulerManager, SingleExecutionSchedulerItem, get_result
from ...constants.callback import CALLBACK_TYPE, EXECUTION_METHOD
from ...types.callback import CallbackItem, CallbackFunction
from ...types.event import BaseEvent
from ...utils.queue import TypedAsyncQueue
from ...utils.worker import ProducerConsumerWorker


PROCESS_EVENT_QUEUE_MAXSIZE = get_config("PROCESS_EVENT_QUEUE_MAXSIZE", 1024)


def new_serial_scheduler(cb_type: str) -> SchedulerManager:
    return SchedulerManager(
        cb_type,
        global_callback_container,
        SingleExecutionSchedulerItem,
        {"execution_method": EXECUTION_METHOD.SERIAL},
        get_result = get_result,
    )

init_scheduler = new_serial_scheduler(CALLBACK_TYPE.INIT)
exit_scheduler = new_serial_scheduler(CALLBACK_TYPE.EXIT)


PROCESS_TYPE_LOGGER = get_logger("ProcessScheduler")

class ProcessSchedulerItem(BaseSchedulerItem):
    def __init__(
            self,
            cb_type: str,
            identifier: str,
            *callbacks: tuple[CallbackItem, ...],
            process_event_queue_maxsize: int = 0,
    ) -> None:
        super().__init__(cb_type, identifier, *callbacks)

        self._worker = ProducerConsumerWorker(
            self._producer,
            self._consumer,
            max(process_event_queue_maxsize, 0),
        )
        self._distributor: TypedAsyncQueue | None = None
        self._event_callback: dict[Type[BaseEvent], set[Callable[[BaseEvent], Awaitable[None]]]] = {}
        self._inherit_cache: dict[Type[BaseEvent], set[Callable[[BaseEvent], Awaitable[None]]]] = {}

    async def _init_event_callback(self) -> None:
        event_types = await asyncio.gather(*(callback.actual_func() for callback in self.callbacks))
        for callback, event_type in zip(self.callbacks, event_types):
            try:
                if issubclass(event_type, BaseEvent):
                    self._event_callback.setdefault(event_type, set()).add(callback.actual_func)
                    continue

            except TypeError:
                pass

            PROCESS_TYPE_LOGGER.warning(f"[{callback.func_name}]: <{event_type}> is not a subclass of <BaseEvent>, this callback function will be ignored.")
            continue

    def _reset_event_callback(self) -> None:
        self._event_callback.clear()
        self._inherit_cache.clear()

    def _get_callbacks(self, event: BaseEvent) -> set[Callable[[BaseEvent], Awaitable[None]]]:
        event_type = event.__class__
        if event_type in self._inherit_cache:
            return self._inherit_cache[event_type]

        cache_callbacks = set()
        for key, callbacks in self._event_callback.items():
            if issubclass(event_type, key):
                cache_callbacks.update(callbacks)

        return cache_callbacks

    async def _producer(self) -> BaseEvent:
        event = await self._distributor.get()
        self._distributor.task_done()
        return event

    async def _consumer(self, event: BaseEvent) -> None:
        callbacks = self._get_callbacks(event)
        if not callbacks:
            return

        await asyncio.gather(*(callback(event) for callback in callbacks))

    async def start(self) -> None:
        if self._worker.is_running():
            return

        await self._init_event_callback()
        if not self._event_callback:
            self._reset_event_callback()
            return

        self._distributor = event_distributor_manager.get_distributor(self.identifier, set(self._event_callback.keys()))
        await self._worker.start()

    async def stop(self, force_stop: bool = False) -> None:
        if not self._worker.is_running():
            return

        await self._worker.stop(force_stop)
        self._reset_event_callback()
        event_distributor_manager.del_distributor(self.identifier)
        self._distributor = None

process_scheduler = SchedulerManager(
    CALLBACK_TYPE.PROCESS,
    global_callback_container,
    ProcessSchedulerItem,
    {"process_event_queue_maxsize": PROCESS_EVENT_QUEUE_MAXSIZE},
)


class AutorunSchedulerItem(BaseSchedulerItem):
    def __init__(
            self,
            cb_type: str,
            identifier: str,
            *callbacks: tuple[CallbackItem, ...],
    ) -> None:
        super().__init__(cb_type, identifier, *callbacks)

        self._run_sign: bool = False
        self._tasks: list[tuple[CallbackFunction, asyncio.Task]] = []

    async def start(self) -> None:
        if self._run_sign:
            return

        self._run_sign = True
        for callback in self.callbacks:
            lock_symbol = callback.origin_func # Function is a hashable object, and the function can be used as a symbol to get the lock from the manager.
            task = asyncio.create_task(callback.actual_func())
            self._tasks.append((lock_symbol, task))

    async def stop(self, force_stop: bool = False) -> None:
        if not self._run_sign:
            return

        self._run_sign = False
        for lock_symbol, task in self._tasks:
            if not force_stop:
                await global_async_completion_lock_manager.wait(lock_symbol)

            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self._tasks.clear()

autorun_scheduler = SchedulerManager(
    CALLBACK_TYPE.AUTORUN,
    global_callback_container,
    AutorunSchedulerItem,
)


__all__ = [
    "init_scheduler",
    "exit_scheduler",
    "process_scheduler",
    "autorun_scheduler",
]
