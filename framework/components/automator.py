from asyncio import Event, Lock, Semaphore, sleep as async_sleep
from typing import Callable, Coroutine, Literal, cast, Hashable, Self

from .executor import BasicExecutor
from .rule.engine import RuleEngine
from ..base.lifecycle import BaseLifeCycle, with_running_check
from ..base.worker import BaseProducerConsumerWorker
from ..types.executor import ExecutorProtocol
from ..types.rule import RuleProtocol
from ..utils.concurrency.asyncio import get_semaphore
from ..utils.dataclass import validation_dataclass, validation_field, new_type_validator
from ..utils.paramtools import params_validator


_TASK_FUNC = Callable[[], Coroutine[None, None, None] | None]
_EXC_CALLBACK = Callable[[Exception], None]


@validation_dataclass(frozen=True)
class _InitParamsDataCls: # For '_SingleAutomator.__init__'.
    self: "_SingleAutomator"
    sem: Semaphore
    task_func: _TASK_FUNC
    wait_rule: RuleProtocol # Hand over to 'RulerEngine' for verification.
    executor: ExecutorProtocol = validation_field(new_type_validator(ExecutorProtocol, BasicExecutor()), default=None)
    exc_callback: _EXC_CALLBACK | None = None # Hand over to 'BaseProducerConsumerWorker' for verification.


class _SingleAutomator(BaseProducerConsumerWorker):
    @params_validator(_InitParamsDataCls)
    def __init__(
            self,
            sem: Semaphore,
            task_func: _TASK_FUNC,
            wait_rule: RuleProtocol,
            executor: ExecutorProtocol | None = None,
            exc_callback: _EXC_CALLBACK | None = None,
    ) -> None:
        super().__init__(
            producer_concurrency=1,
            consumer_concurrency=1,
            consumer_exc_callback=exc_callback,
        )

        self._rule_engine = RuleEngine(wait=wait_rule)
        self._token = Event()

        # The 'consumer_executor' logic of Worker is not reused here.
        # Since the consumer needs to accept one parameter, a special handling branch is implemented here.
        consumer_executor = cast(ExecutorProtocol, executor)
        wrapped_task_func = consumer_executor(task_func)
        async def consumer(data) -> None:
            async with sem:
                is_success, exc = await wrapped_task_func()
                self._token.set()
                if not is_success:
                    raise exc # Propagate upwards and hand over to the Worker's exception handling logic.
        self.consumer = consumer

    async def producer(self) -> Literal[True]:
        await self._token.wait()
        self._token.clear()
        await async_sleep(self._rule_engine.wait)
        return True

    async def consumer(self, data) -> None: # Placeholder function to allow AbstractClass to be instantiated.
        pass

    async def real_start(self) -> None:
        self._token.set()
        await super().real_start()

    async def real_stop(self, force: bool = False) -> None:
        await super().real_stop(force)
        self._rule_engine.reset()


class Automator(BaseLifeCycle):
    """
    Usage:
        def task1() -> None:
            print("I'm Task1!")

        async def task2() -> None:
            print("I'm Task2!")

        async def task3() -> None:
            print("I'm Task3!")

        def exc_callback(exc: Exception) -> None:
            print(f"I'm exception! {exc}")

        automator = Automator(max_concurrent=2) # If this value is 0, there is no limit on concurrency.
        await automator.start() # Non-blocking startup.
        await automator.register("task1's symbol", task1, task1_wait_rule) # Supports both synchronous and asynchronous functions.
        await automator.register("task2's symbol", task2, task2_wait_rule, task2_executor) # You may use a separate executor for each task.
        await automator.register("task3's symbol", task3, task3_wait_rule, task3_executor, exc_callback) # Note: 'exc_callback' does not support asynchronous functions.

        await automator.cancel("task1's symbol", force=False) # Symbol is used to cancel task. If there is no corresponding task for the symbol, this method will not raise an exception.
        await automator.stop(force=False) # This method will cancel all tasks. You can specify 'force=True' to force stop and cancel all tasks.
    """
    def __init__(self, max_concurrent: int = 0):
        super().__init__()

        self._automator_item_map: dict[Hashable, _SingleAutomator] = {}
        self._reg_lock = Lock()
        self._sem = get_semaphore(max_concurrent, bounded=False) # If this value is 0, there is 'UnlimitedSemaphore'.

    @with_running_check(True)
    async def register(
            self: Self,
            symbol: Hashable,
            task_func: _TASK_FUNC,
            wait_rule: RuleProtocol,
            executor: ExecutorProtocol | None = None,
            exc_callback: _EXC_CALLBACK | None = None,
    ) -> None:
        async with self._reg_lock:
            if symbol in self._automator_item_map:
                raise RuntimeError(f"Symbol '{symbol}' already used")
            hash(symbol)
            await (automator_item := _SingleAutomator(self._sem, task_func, wait_rule, executor, exc_callback)).start()
            self._automator_item_map[symbol] = automator_item

    async def _no_running_check_cancel(self: Self, symbol: Hashable, force: bool = False) -> None:
        async with self._reg_lock:
            if symbol not in self._automator_item_map:
                return
            await self._automator_item_map.pop(symbol).stop(force)

    cancel = with_running_check(True)(_no_running_check_cancel)

    async def real_start(self) -> None:
        pass

    async def real_stop(self, force: bool = False) -> None:
        for symbol in list(self._automator_item_map.keys()):
            await self._no_running_check_cancel(symbol, force)


__all__ = [
    "Automator",
]
