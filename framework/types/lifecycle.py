from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class LifeCycleProtocol(Protocol):
    @property
    @abstractmethod
    def running(self) -> bool: ...

    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self, force: bool = False) -> None: ...


__all__ = [
    "LifeCycleProtocol",
]
