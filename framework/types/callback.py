from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Type

from .event import BaseEvent
from ..base.trigger import BaseTrigger
from ..components.trigger import EmptyTrigger


CallbackFunction = Callable[..., Any | Awaitable[Any]]

_Registrar = Callable[[CallbackFunction], CallbackFunction]

CallbackRegistrar = Callable[..., _Registrar] | _Registrar


FunctionIdentifierGetter = Callable[[CallbackFunction], str]

FunctionNameGetter = Callable[[CallbackFunction], str]


@dataclass(frozen=True)
class CallbackItem:
    type: str
    identifier: str
    func_name: str
    origin_func: CallbackFunction
    actual_func: CallbackFunction


@dataclass(frozen=True)
class CallbackResultItem:
    item: CallbackItem
    is_exit: bool
    is_success: bool
    result: Any


@dataclass(frozen=True)
class BaseArgs:
    origin_func: CallbackFunction
    func_name: str
    identifier: str


@dataclass(frozen=True)
class BaseCallbackExecutorArgs(BaseArgs):
    pass


@dataclass(frozen=True)
class BaseCallbackWrapperArgs(BaseArgs):
    pass


@dataclass(frozen=True)
class BuiltinEmptyExecutorArgs(BaseCallbackExecutorArgs):
    pass


@dataclass(frozen=True)
class BuiltinExecutorArgs(BaseCallbackExecutorArgs):
    timeout: int = 0
    retry_num: int = 0
    retry_interval: int = 0


@dataclass(frozen=True)
class BuiltinEmptyWrapperArgs(BaseCallbackWrapperArgs):
    pass


@dataclass(frozen=True)
class BuiltinProcessWrapperArgs(BaseCallbackWrapperArgs):
    event_type: Type[BaseEvent] = BaseEvent


@dataclass(frozen=True)
class BuiltinAutorunWrapperArgs(BaseCallbackWrapperArgs):
    trigger: BaseTrigger = EmptyTrigger()
    no_safe_exit: bool = isinstance(trigger, EmptyTrigger)


__all__ = [
    "CallbackFunction",
    "CallbackRegistrar",

    "FunctionIdentifierGetter",
    "FunctionNameGetter",

    "CallbackItem",
    "CallbackResultItem",

    "BaseArgs",
    "BaseCallbackExecutorArgs",
    "BaseCallbackWrapperArgs",

    "BuiltinEmptyExecutorArgs",
    "BuiltinExecutorArgs",
    "BuiltinEmptyWrapperArgs",
    "BuiltinProcessWrapperArgs",
    "BuiltinAutorunWrapperArgs",
]
