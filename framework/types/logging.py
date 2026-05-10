from abc import abstractmethod
from logging import Logger
from typing import Protocol, runtime_checkable


@runtime_checkable
class HasLoggerProtocol(Protocol):
    @property
    @abstractmethod
    def logger(self) -> Logger:
        pass

    @abstractmethod
    def set_logger(self, logger: Logger | str | None = None) -> None:
        """
        :param logger: If this parameter is None, set logger to default.
        """
        pass


__all__ = [
    "HasLoggerProtocol",
]
