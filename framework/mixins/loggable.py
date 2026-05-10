from logging import Formatter, Logger, StreamHandler, getLogger
from typing import Self

from ..types.logging import HasLoggerProtocol


_default_handler = StreamHandler()
_default_handler.setLevel("DEBUG")
_default_handler.setFormatter(Formatter("[%(levelname)s] %(asctime)s [%(name)s<%(filename)s:%(lineno)d>] - %(message)s"))


def _get_logger(name: str) -> Logger:
    logger = getLogger(name)
    if logger.hasHandlers():
        return logger
    logger.propagate = False
    logger.setLevel("DEBUG")
    logger.addHandler(_default_handler)
    return logger


class LoggableMixin(HasLoggerProtocol):
    def __new__(cls, *_, **__) -> Self:
        instance = super().__new__(cls)
        instance.set_logger()
        return instance

    def set_logger(self, logger: Logger | str | None = None) -> None:
        if logger is None:
            self._logger = _get_logger(type(self).__name__)
        elif isinstance(logger, Logger):
            self._logger = logger
        elif isinstance(logger, str):
            self._logger = _get_logger(logger)
        else:
            raise TypeError("Unsupported logger type")

    @property
    def logger(self) -> Logger:
        return self._logger


__all__ = [
    "LoggableMixin",
]
