from abc import ABC, abstractmethod


class BaseTrigger(ABC):
    @abstractmethod
    async def wait(self) -> None: ...


__all__ = [
    "BaseTrigger",
]
