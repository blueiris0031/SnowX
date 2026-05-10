from typing import Callable


class ExceptionSignal(Exception):
    def __init__(self, task: Callable, exc: Exception, critical: bool = False):
        super().__init__()

        self.task = task
        self.exc = exc
        self.critical = critical


class StopSignal(Exception):
    pass


__all__ = [
    "ExceptionSignal",
    "StopSignal",
]
