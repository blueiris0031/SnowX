from abc import abstractmethod
from typing import Callable, Coroutine, Literal, ParamSpec, Protocol, TypeVar, overload, runtime_checkable


_P = ParamSpec("_P")
_R = TypeVar("_R")
_FAIL_RET = tuple[Literal[False] , Exception]


@runtime_checkable
class ExecutorProtocol(Protocol):
    @overload
    def __call__(
            self,
            func: Callable[_P, Coroutine[None, None, _R] | _R],
    ) -> Callable[_P, Coroutine[None, None, tuple[Literal[True], _R] | _FAIL_RET]]: ...

    @overload
    def __call__(
            self,
            func: None = None,
    ) -> Callable[[Callable[_P, Coroutine[None, None, _R] | _R]], Callable[_P, Coroutine[None, None, tuple[Literal[True], _R] | _FAIL_RET]]]: ...

    @abstractmethod
    def __call__(
            self,
            func: Callable[_P, Coroutine[None, None, _R] | _R] | None = None,
    ) -> Callable[_P, Coroutine[None, None, tuple[Literal[True], _R] | _FAIL_RET]] | Callable[[Callable[_P, Coroutine[None, None, _R] | _R]], Callable[_P, Coroutine[None, None, tuple[Literal[True], _R] | _FAIL_RET]]]: ...


@runtime_checkable
class HasExecutorProtocol(Protocol):
    @property
    @abstractmethod
    def executor(self) -> ExecutorProtocol:
        pass

    @abstractmethod
    def set_executor(self, executor: ExecutorProtocol | None = None) -> None:
        """
        :param executor: If this parameter is None, set executor to default.
        """
        pass


__all__ = [
    "ExecutorProtocol",
    "HasExecutorProtocol",
]
