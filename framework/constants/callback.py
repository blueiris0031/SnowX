from asyncio import gather
from dataclasses import dataclass
from typing import Callable, Awaitable, Any

from ..utils.serial_executor import serial_executor


@dataclass(frozen=True)
class CallbackType:
    INIT: str = "init"
    EXIT: str = "exit"
    PROCESS: str = "process"
    AUTORUN: str = "autorun"


CALLBACK_TYPE = CallbackType()


@dataclass(frozen=True)
class ExecutionMethod:
    SERIAL: Callable[..., Awaitable[tuple[Any, ...]]] = serial_executor
    PARALLEL: Callable[..., Awaitable[tuple[Any, ...]]] = gather


EXECUTION_METHOD = ExecutionMethod()


__all__ = [
    "CALLBACK_TYPE",
    "EXECUTION_METHOD",
]
