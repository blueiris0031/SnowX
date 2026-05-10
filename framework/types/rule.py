from abc import abstractmethod
from numbers import Real
from typing import Protocol, runtime_checkable


@runtime_checkable
class RuleProtocol(Protocol):
    @abstractmethod
    def __call__(self, count: int) -> Real:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass


__all__ = [
    "RuleProtocol",
]
