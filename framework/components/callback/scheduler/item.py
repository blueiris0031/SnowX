import asyncio
import uuid
from typing import Any, Awaitable, Callable, TypeVar

from ...automator import Automator
from ...distributor import TypedObjectDistributor
from ...ruler.ruler import FixedRuler
from ....base.callback import BaseSchedulerItem
from ....constants.callback import EXECUTION_MODE
from ....types.callback import CallbackResultItem
from ....utils.queue import TypedAsyncQueue
from ....utils.worker import BaseProducerConsumerWorker


class SingleExecutionItem(BaseSchedulerItem):
    def __init__(
            self,
            execution_mode: Callable[..., Awaitable[tuple[Any, ...]]] = EXECUTION_MODE.PARALLEL, # default to use asyncio.gather
            *args,
            **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        self._execution_mode = execution_mode
        self._run_sign = asyncio.Event()
        self._run_sign.set()

        self._result_fut: asyncio.Future[tuple[CallbackResultItem, ...]] = asyncio.get_running_loop().create_future()

    async def producer(self) -> bool:
        await self._run_sign.wait()
        self._run_sign.clear()
        return True

    async def consumer(self, _) -> Any:
        results = await self._execution_mode(
            *(
                self._executor(callback.func, **callback.extra_kwargs)()
                for callback in self.callbacks
            ),
            return_exceptions=True
        )

        self._result_fut.set_result(
            tuple(
                CallbackResultItem(
                    callback,
                    result[0] if isinstance(result, tuple) else False,
                    result[1] if isinstance(result, tuple) else result,
                )
                for callback, result in zip(self.callbacks, results)
            )
        )

    async def get_result(self) -> tuple[CallbackResultItem, ...]:
        return await self._result_fut


_O = TypeVar("_O", bound=object)
_C = TypeVar("_C", bound=Callable)


class _SingleProcessItem(BaseProducerConsumerWorker):
    def __init__(
            self,
            wrapped: Callable[[_O], Awaitable[tuple[bool, tuple[_O, ...] | _O | None]]],
            source: TypedAsyncQueue,
            output: Callable[[tuple[_O, ...] | _O | None], Awaitable[None]],
            maximum_concurrents: int = 0,
    ):
        super().__init__(maximum_concurrents)

        self._wrapped = wrapped
        self._source = source
        self._output = output

    async def producer(self) -> _O:
        return await self._source.get()

    async def consumer(self, data: _O) -> None:
        is_success, result = await self._wrapped(data)
        if not is_success:
            return
        await self._output(result)


class ProcessTypeItem(BaseSchedulerItem):
    def __init__(
            self,
            distributor: TypedObjectDistributor,
            maximum_concurrents: int = 0,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._distributor = distributor
        self._distributor_map: dict[str, _SingleProcessItem] = {
            (symbol := uuid.uuid4().hex): _SingleProcessItem(
                wrapped,
                self._distributor.subscribe(
                    symbol,
                    *(extra_kwargs := callback.extra_kwargs).get("allow_types", ()),
                    custom_checker=extra_kwargs.get("custom_checker", None),
                    strict_mode=extra_kwargs.get("strict_mode", False),
                ),
                self._distributor.put_object,
                maximum_concurrents
            ) for callback, wrapped in self.wrapped_callbacks
        }

    async def producer(self) -> None:
        event = asyncio.Event()
        event.clear()
        await event.wait()

    async def consumer(self, _) -> None:
        pass

    async def start(self) -> None:
        for s_item in self._distributor_map.values():
            await s_item.start()
        await super().start()

    async def stop(self, force_stop: bool = False) -> None:
        for symbol, s_item in self._distributor_map.items():
            self._distributor.unsubscribe(symbol)
            await s_item.stop(force_stop)
        await super().stop(force_stop)


class AutorunTypeItem(BaseSchedulerItem):
    def __init__(
            self,
            distributor: TypedObjectDistributor,
            *args,
            **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        self._distributor = distributor
        self._automator = Automator(
            *(
                (
                    self._automator_task_wrapper(base_wrapped),
                    callback.extra_kwargs.get("automatic_ruler", FixedRuler(0))
                ) for callback, base_wrapped in self.wrapped_callbacks
            )
        )

    def _automator_task_wrapper(self, func: Callable[[], ...]) -> Callable[[], Awaitable[None]]:
        async def wrapped() -> None:
            is_success, result = await func()
            if not is_success:
                return
            await self._distributor.put_object(result)
        return wrapped

    async def producer(self) -> None:
        event = asyncio.Event()
        event.clear()
        await event.wait()

    async def consumer(self, _) -> None:
        pass

    async def start(self) -> None:
        await super().start()
        await self._automator.start()


__all__ = [
    "SingleExecutionItem",
    "ProcessTypeItem",
    "AutorunTypeItem",
]
