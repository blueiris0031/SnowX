from asyncio import Event, Queue, Runner
from functools import partial
from sys import stderr
from typing import Callable, Coroutine, Literal, Self

from ..base.lifecycle import BaseLifeCycle, with_running_check
from ..components.automator import Automator
from ..components.rule.rule import FixedValueRule
from ..constants.logger import ROOT_NAME
from ..error.kernel import ExceptionSignal, StopSignal
from ..mixins.executor import ExecutorMixin
from ..mixins.loggable import LoggableMixin
from ..types.kernel.basic_kernel import BasicKernelProtocol
from ..types.loop import with_loop_check
from ..utils.lock import ExclusiveLock
from ..utils.singleton import singleton_decorator


def _ffff0():
    """
    Pull up the initialization pipeline. \n
    This function should not be called externally.
    """
    from .bootstrap import _7c00

    basic_kernel = BasicKernel()
    basic_kernel.submit_task(partial(_7c00, basic_kernel), True)


_TASK_FUNC = Callable[[], Coroutine[None, None, None] | None]
_TASK = tuple[_TASK_FUNC, bool]


@singleton_decorator
class BasicKernel(BaseLifeCycle, ExecutorMixin, LoggableMixin, BasicKernelProtocol):
    """
    Warning: This BasicKernel must not be accessed directly.
    """

    _task_handler_symbol: Literal[0] = 0
    _callback_handler_symbol: Literal[1] = 1

    def __init__(self):
        super().__init__(pre_start_modify_running_flag=True)

        self._automator = Automator()
        self._panic_callback_queue: Queue[_TASK] = Queue()
        self._stop_callback_queue: Queue[_TASK] = Queue()
        self._task_queue: Queue[_TASK] = Queue()

        self._stop_event = Event()
        self._panic = False

        self.set_logger(f"{ROOT_NAME}.basic_kernel")

    def _new_handler(self, task_queue: Queue[_TASK], logging_type: str) -> Callable[[], Coroutine[None, None, None]]:
        async def handler() -> None:
            task, critical = await task_queue.get()
            is_success, exc = await self.executor(task)()
            self.logger.debug("Execution status: %s(Type: %s, Critical: %s, Success: %s)", task, logging_type, critical, is_success)
            task_queue.task_done()
            if not is_success:
                raise ExceptionSignal(task, exc, critical)
        return handler

    def _task_exc_handler(self, exception: Exception) -> None:
        if not isinstance(exception, ExceptionSignal):
            self.logger.error("Unknown type of exception.", exc_info=exception)
            return

        task, exc, critical = exception.task, exception.exc, exception.critical
        if isinstance(exc, StopSignal):
            self.logger.info("Received stop signal from task: %s", task)
            self._stop_event.set()
            return

        if not critical:
            self.logger.error("An exception was raised during task execution: %s", task, exc_info=exc)
            return

        self.logger.critical("An exception was raised during critical task execution: %s", task, exc_info=exc)
        self._panic = True
        self._stop_event.set()

    def _callback_exc_handler(self, exception: Exception) -> None:
        if not isinstance(exception, ExceptionSignal):
            self.logger.error("An exception was raised during callback execution.", exc_info=exception)
        else:
            self.logger.error("An exception was raised during callback execution: %s", exception.task, exc_info=exception.exc)

    @staticmethod
    def _clear(task_queue: Queue[_TASK]) -> None:
        while not task_queue.empty():
            task_queue.get_nowait()
            task_queue.task_done()

    async def _callback_handler(self, queue: Queue[_TASK]) -> None:
        await self._automator.register(
            self._callback_handler_symbol,
            self._new_handler(queue, "Callback"),
            FixedValueRule(0),
            exc_callback=self._callback_exc_handler,
        )
        await queue.join()
        await self._automator.cancel(self._callback_handler_symbol)

    async def real_start(self) -> None:
        await self._automator.start()
        self._stop_event.clear()
        self.submit_task(_ffff0, critical=True)  # First command.
        await self._automator.register(
            self._task_handler_symbol,
            self._new_handler(self._task_queue, "Task"),
            FixedValueRule(0),
            exc_callback=self._task_exc_handler,
        )
        self.logger.info("Started.")

    async def _normal_stop(self) -> None:
        await self._task_queue.join()
        await self._automator.cancel(self._task_handler_symbol)

        await self._callback_handler(self._stop_callback_queue)
        self._clear(self._panic_callback_queue)
        await self._automator.stop()
        self.logger.info("Stopped.")

    async def _panic_stop(self) -> None:
        await self._automator.cancel(self._task_handler_symbol, True)

        await self._callback_handler(self._panic_callback_queue)
        self._clear(self._task_queue)
        self._clear(self._stop_callback_queue)
        await self._automator.stop(True)
        self.logger.critical("Panicked.")

    async def real_stop(self, force: bool = False) -> None:
        self._stop_event.set()
        if force or self._panic:
            await self._panic_stop()
        else:
            await self._normal_stop()

    @with_loop_check
    @with_running_check(True)
    def submit_task(self: Self, task: _TASK_FUNC, critical: bool = False) -> None:
        """
        Note: Only tasks related to kernel state are permitted to be submitted; tasks related to business logic are strictly prohibited.
        """
        self.logger.debug("Received submitted task: %s(Critical: %s)", task, critical)
        self._task_queue.put_nowait((task, critical))

    @with_loop_check
    @with_running_check(True)
    def submit_stop_callback(self: Self, task: _TASK_FUNC) -> None:
        """
        Note: If the submitted callback is blocked, it may cause a deadlock in 'BasicKernel'.
        """
        self.logger.debug("Received submitted callback: %s(Type: Stop)", task)
        self._stop_callback_queue.put_nowait((task, False))

    @with_loop_check
    @with_running_check(True)
    def submit_panic_callback(self: Self, task: _TASK_FUNC) -> None:
        """
        Note: If the submitted callback is blocked, it may cause a deadlock in 'BasicKernel'.
        """
        self.logger.debug("Received submitted callback: %s(Type: Panic)", task)
        self._panic_callback_queue.put_nowait((task, False))

    async def start(self) -> None:
        """
        This function should not be called externally.
        """
        await super().start()

    async def stop(self, force: bool = False) -> None:
        """
        This function should not be called externally.
        """
        await super().stop(force)

    async def main(self) -> None:
        """
        This function should not be called externally.
        """
        await self.start()
        await self._stop_event.wait()
        await self.stop()


_exclusive_lock = ExclusiveLock()


def main():
    with _exclusive_lock:
        print("Ready to boot 'BasicKernel'.", file=stderr)

        # This function is necessary, because LoopBoundMixin binds the running loop in __new__.
        async def _por() -> None: await BasicKernel().main()
        with Runner() as runner:
            runner.run(_por())


__all__ = [
    "main",
]
