from abc import abstractmethod
from asyncio import CancelledError, Queue, Task, create_task
from traceback import print_exception
from typing import Any, Callable, Coroutine, cast

from ..base.lifecycle import BaseLifeCycle
from ..components.executor import BasicExecutor
from ..types.executor import ExecutorProtocol
from ..utils.concurrency.asyncio import AsyncWaitGroup
from ..utils.dataclass import validation_dataclass, validation_field, new_type_validator
from ..utils.paramtools import params_validator
from ..utils.void import VoidClass, ASYNC_CONTEXT_MANAGER_TEMPLATE


class _Void(VoidClass, **ASYNC_CONTEXT_MANAGER_TEMPLATE):
    """
    VoidAsyncContextManager+VoidAsyncQueue
    """
    pass


_EXC_CALLBACK = Callable[[Exception], None]


_executor_validator = new_type_validator(ExecutorProtocol, BasicExecutor())
_exc_callback_validator = new_type_validator(Callable, print_exception)
def _concurrency_validator(val: int) -> int:
    if (int_val := int(val)) <= 0:
        raise ValueError("Concurrency must be positive integer")
    return int_val


@validation_dataclass(frozen=True)
class _InitParamsDataCls: # For 'BaseProducerConsumerWorker'.
    self: Any
    data_buffer_length: int = validation_field(int, default=64)
    producer_concurrency: int = validation_field(_concurrency_validator, default=1)
    producer_executor: ExecutorProtocol = validation_field(_executor_validator, default=None)
    producer_exc_callback: _EXC_CALLBACK = validation_field(_exc_callback_validator, default=None)
    consumer_concurrency: int = validation_field(_concurrency_validator, default=8)
    consumer_executor: ExecutorProtocol = validation_field(_executor_validator, default=None)
    consumer_exc_callback: _EXC_CALLBACK = validation_field(_exc_callback_validator, default=None)


class BaseProducerConsumerWorker(BaseLifeCycle):
    _poison = object()

    @params_validator(_InitParamsDataCls)
    def __init__(
            self,
            data_buffer_length: int = 64,
            producer_concurrency: int = 1,
            producer_executor: ExecutorProtocol | None = None,
            producer_exc_callback: _EXC_CALLBACK | None = None,
            consumer_concurrency: int = 8,
            consumer_executor: ExecutorProtocol | None = None,
            consumer_exc_callback: _EXC_CALLBACK | None = None,
    ) -> None:
        """
        Note: If exc_callback raised an exception, it will cause WorkerLoop to crash.
        :param data_buffer_length: Backpressure buffer queue length. If this parameter is not a positive integer, there is no length limit.
        :param producer_concurrency: Producer concurrency.
        :param producer_executor: 'executor' for executing the 'producer'. 'BasicExecutor' is used by default.
        :param producer_exc_callback: This callback will be triggered with the Exception object passed as an argument when the 'producer' raises an Exception. Async functions are not supported.
        :param consumer_concurrency: Consumer concurrency.
        :param consumer_executor: 'executor' for executing the 'consumer'. 'BasicExecutor' is used by default.
        :param consumer_exc_callback: This callback will be triggered with the Exception object passed as an argument when the 'consumer' raises an Exception. Async functions are not supported.
        """
        super().__init__(pre_start_modify_running_flag=True, pre_stop_modify_running_flag=True)

        self._data_buffer_length = data_buffer_length
        self._producer_concurrency = producer_concurrency
        self._producer_executor = cast(ExecutorProtocol, producer_executor)
        self._producer_exc_callback = cast(_EXC_CALLBACK, producer_exc_callback)
        self._consumer_concurrency = consumer_concurrency
        self._consumer_executor = cast(ExecutorProtocol, consumer_executor)
        self._consumer_exc_callback = cast(_EXC_CALLBACK, consumer_exc_callback)

        self._data_queue: Queue | _Void = _Void()
        self._data_submission_wg: AsyncWaitGroup | _Void = _Void()

        self._producer_task_pool: list[Task] = []
        self._consumer_task_pool: list[Task] = []

    @abstractmethod
    def producer(self) -> Coroutine[None, None, Any] | Any:
        """
        Supports both ordinary function and asynchronous function. \n
        Note: If the default 'BasicExecutor' is used, it is recommended to use asynchronous functions; otherwise, Workers may fail to work properly.
        """
        pass

    @abstractmethod
    def consumer(self, data: Any) -> Coroutine[None, None, None] | None:
        """
        Supports both ordinary function and asynchronous function.
        """
        pass

    async def _producer_loop(self) -> None:
        producer = self._producer_executor(self.producer)
        while self.running:
            is_success, result = await producer()
            if not is_success:
                self._producer_exc_callback(result)
                continue
            async with self._data_submission_wg:
                await self._data_queue.put(result)

    async def _start_producer(self):
        for _ in range(self._producer_concurrency):
            self._producer_task_pool.append(create_task(self._producer_loop()))

    async def _stop_producer(self, force: bool = False) -> None:
        if not force:
            await self._data_submission_wg.wait()
        while self._producer_task_pool:
            task = self._producer_task_pool.pop()
            task.cancel()
            try:
                await task
            except CancelledError:
                pass

    async def _consumer_loop(self) -> None:
        consumer = self._consumer_executor(self.consumer)
        while True:
            data = await self._data_queue.get()
            if data is self._poison:
                self._data_queue.task_done()
                break
            is_success, result = await consumer(data)
            if not is_success:
                self._consumer_exc_callback(result)
            self._data_queue.task_done()

    async def _start_consumer(self) -> None:
        for _ in range(self._consumer_concurrency):
            self._consumer_task_pool.append(create_task(self._consumer_loop()))

    async def _stop_consumer(self, force: bool = False) -> None:
        if not force:
            for _ in range(self._consumer_concurrency):
                await self._data_queue.put(self._poison)
            await self._data_queue.join()
        while self._consumer_task_pool:
            task = self._consumer_task_pool.pop()
            task.cancel()
            try:
                await task
            except CancelledError:
                pass

    async def real_start(self) -> None:
        self._data_queue = Queue(self._data_buffer_length)
        self._data_submission_wg = AsyncWaitGroup()
        await self._start_consumer()
        await self._start_producer()

    async def real_stop(self, force: bool = False) -> None:
        await self._stop_producer(force)
        await self._stop_consumer(force)
        self._data_submission_wg = _Void()
        self._data_queue = _Void()


__all__ = [
    "BaseProducerConsumerWorker",
]
