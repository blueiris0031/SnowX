import asyncio
from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Coroutine, Literal, ParamSpec, TypeVar

from ..types.executor import ExecutorProtocol


_P = ParamSpec("_P")
_R = TypeVar("_R")
_FAIL_RET = tuple[Literal[False] , Exception]


class BaseExecutor(ExecutorProtocol):
    def __call__(
            self,
            func: Callable[_P, Coroutine[None, None, _R] | _R] | None = None,
    ) -> Callable[_P, Coroutine[None, None, tuple[Literal[True], _R] | _FAIL_RET]] | Callable[[Callable[_P, Coroutine[None, None, _R] | _R]], Callable[_P, Coroutine[None, None, tuple[Literal[True], _R] | _FAIL_RET]]]:
        def interior_decorator(func_: Callable[_P, Coroutine[None, None, _R] | _R]) -> Callable[_P, Coroutine[None, None, tuple[Literal[True], _R] | _FAIL_RET]]:
            return wraps(func_)(self.wrapper(func_))
        if func is None:
            return interior_decorator
        return interior_decorator(func)

    @staticmethod
    def sync_wrapper(func: Callable[_P, _R]) -> Callable[_P, Coroutine[None, None, _R]]:
        """
        This wrapper needs to wrap synchronous functions and return an asynchronous function. /n
        The default implementation does not use to_thread. Rewrite this method if needed.
        """
        async def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            return func(*args, **kwargs)
        return wrapped

    @staticmethod
    def async_wrapper(func: Callable[_P, Coroutine[None, None, _R]]) -> Callable[_P, Coroutine[None, None, _R]]:
        """
        The default implementation is empty. Rewrite this method if needed.
        """
        return func

    @staticmethod
    def logic_wrapper(func: Callable[_P, Coroutine[None, None, _R]]) -> Callable[_P, Coroutine[None, None, _R]]:
        """
        This wrapper determines the execution logic of func. /n
        The default implementation is empty. Rewrite this method if needed.
        """
        return func

    @staticmethod
    def ret_wrapper(func: Callable[_P, Coroutine[None, None, _R]]) -> Callable[_P, Coroutine[None, None, tuple[Literal[True], _R] | _FAIL_RET]]:
        """
        This wrapper defines the logic for handling the return values or exceptions of func. /n
        If you rewrite this method, ensure the return value is 'tuple[Literal[True], result] | tuple[Literal[False], Exception]'.
        """
        async def wrapped(*func_args: _P.args, **func_kwargs: _P.kwargs) -> tuple[Literal[True], _R] | _FAIL_RET:
            try:
                return True, await func(*func_args, **func_kwargs)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                return False, e
        return wrapped

    def wrapper(
            self,
            func: Callable[_P, Coroutine[None, None, _R] | _R],
    ) -> Callable[_P, Coroutine[None, None, tuple[Literal[True], _R] | _FAIL_RET]]:
        if iscoroutinefunction(func):
            func = self.async_wrapper(func)
        else:
            func = self.sync_wrapper(func)
        return self.ret_wrapper(self.logic_wrapper(func))


__all__ = [
    "BaseExecutor",
]
