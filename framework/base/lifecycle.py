from abc import abstractmethod
from asyncio import Lock
from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Coroutine, ParamSpec, Self, TypeVar, cast

from ..components.executor import BasicExecutor
from ..mixins.loop_bound import LoopBoundMixin
from ..types.executor import ExecutorProtocol
from ..types.lifecycle import LifeCycleProtocol
from ..types.loop import with_loop_check
from ..utils.dataclass import new_type_validator, validation_dataclass, validation_field
from ..utils.paramtools import params_validator


_executor_validator = new_type_validator(ExecutorProtocol, BasicExecutor())


@validation_dataclass(frozen=True)
class _InitParamsDataCls: # For 'BaseLifeCycle.__init__'.
    self: "BaseLifeCycle"
    start_executor: ExecutorProtocol = validation_field(_executor_validator, default=None)
    stop_executor: ExecutorProtocol = validation_field(_executor_validator, default=None)
    stop_on_start_failed: bool = validation_field(bool, default=True)
    force_stop_on_start_failed: bool = validation_field(bool, default=False)
    pre_start_modify_running_flag: bool = validation_field(bool, default=False)
    pre_stop_modify_running_flag: bool = validation_field(bool, default=True)


class BaseLifeCycle(LifeCycleProtocol, LoopBoundMixin):
    @params_validator(_InitParamsDataCls)
    def __init__(
            self,
            start_executor: ExecutorProtocol | None = None,
            stop_executor: ExecutorProtocol | None = None,
            stop_on_start_failed: bool = True,
            force_stop_on_start_failed: bool = False,
            pre_start_modify_running_flag: bool = False,
            pre_stop_modify_running_flag: bool = True,
    ) -> None:
        """
        :param start_executor: Executor used to execute 'real_start'; 'BasicExecutor' is used by default.
        :param stop_executor: Executor used to execute 'real_stop'; 'BasicExecutor' is used by default.
        :param stop_on_start_failed: If this parameter is True, the 'real_stop' method will be executed automatically when the 'real_start' method fails to execute.
         Note: Any Exception thrown upon failed execution of 'real_stop' will be ignored.
        :param force_stop_on_start_failed: This parameter determines whether to pass 'force=True' when performing a stop upon startup failure.
         Note: This parameter has no effect when 'stop_on_start_failed' is False.
        :param pre_start_modify_running_flag: If this parameter is True, 'running_flag' will be modified before 'real_start' is executed.
        :param pre_stop_modify_running_flag: If this parameter is True, 'running_flag' will be modified before 'real_stop' is executed.
         Note: This parameter also affects the flag modify behavior when stop is executed after startup failure.
        """
        self._start_executor = cast(ExecutorProtocol, start_executor)
        self._stop_executor = cast(ExecutorProtocol, stop_executor)
        self._stop_on_start_failed = stop_on_start_failed
        self._force_stop_on_start_failed = force_stop_on_start_failed
        self._pre_start_modify_running_flag = pre_start_modify_running_flag
        self._pre_stop_modify_running_flag = pre_stop_modify_running_flag

        self._lifecycle_lock = Lock()
        self._running_flag: bool = False

    @property
    def running(self) -> bool:
        """
        Running flag.
        """
        return self._running_flag

    @abstractmethod
    def real_start(self) -> Coroutine[None, None, None] | None:
        """
        Supports both ordinary function and asynchronous function.
        """
        pass

    @abstractmethod
    def real_stop(self, force: bool = False) -> Coroutine[None, None, None] | None:
        """
        Supports both ordinary function and asynchronous function.
        """
        pass

    async def _start_with_executor(self):
        return await self._start_executor(self.real_start)()

    async def _stop_with_executor(self, force: bool = False):
        return await self._stop_executor(self.real_stop)(force)

    @with_loop_check
    async def start(self: Self) -> None:
        async with self._lifecycle_lock:
            if self._running_flag:
                return

            if self._pre_start_modify_running_flag:
                self._running_flag = True
            is_success, exc = await self._start_with_executor()
            if is_success:
                self._running_flag = True
                return
            if not self._stop_on_start_failed:
                self._running_flag = False
                raise exc
            if self._pre_stop_modify_running_flag:
                self._running_flag = False
            await self._stop_with_executor(self._force_stop_on_start_failed)
            self._running_flag = False
            raise exc

    @with_loop_check
    async def stop(self: Self, force: bool = False) -> None:
        async with self._lifecycle_lock:
            if not self._running_flag:
                return

            if self._pre_stop_modify_running_flag:
                self._running_flag = False
            is_success, exc = await self._stop_with_executor(force)
            self._running_flag = False
            if not is_success:
                raise exc


_P = ParamSpec("_P")
_R = TypeVar("_R")


def with_running_check(running: bool) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """
    For use with 'BaseLifeCycle'
    """
    def wrapper(method: Callable[_P, _R]) -> Callable[_P, _R]:
        if iscoroutinefunction(method):
            async def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                if args[0].running is not running:
                    raise RuntimeError(f"Excepted 'running' is '{running}', but it is currently '{not running}'")
                return await method(*args, **kwargs)
        else:
            def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                if args[0].running is not running:
                    raise RuntimeError(f"Excepted 'running' is '{running}', but it is currently '{not running}'")
                return method(*args, **kwargs)
        return wraps(method)(wrapped)
    return wrapper


__all__ = [
    "BaseLifeCycle",
    "with_running_check",
]
