from abc import abstractmethod
from typing import Protocol, runtime_checkable
from asyncio import AbstractEventLoop, get_running_loop
from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, ParamSpec, TypeVar


@runtime_checkable
class HasLoopProtocol(Protocol):
    @property
    @abstractmethod
    def loop(self) -> AbstractEventLoop:
        pass

    @abstractmethod
    def set_loop(self, loop: AbstractEventLoop | None = None) -> None:
        """
        :param loop: If this parameter is None, set loop to the current thread's running loop.
        """
        pass


_P = ParamSpec("_P")
_R = TypeVar("_R")


def with_loop_check(method: Callable[_P, _R]) -> Callable[_P, _R]:
    """
    For use with 'HasLoopProtocol'.
    """
    if iscoroutinefunction(method):
        async def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            if args[0].loop is not get_running_loop():
                raise RuntimeError("The current running_loop does not match the one bound to this instance")
            return await method(*args, **kwargs)
    else:
        def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            if args[0].loop is not get_running_loop():
                raise RuntimeError("The current running_loop does not match the one bound to this instance")
            return method(*args, **kwargs)
    return wraps(method)(wrapped)


__all__ = [
    "HasLoopProtocol",
    "with_loop_check",
]
