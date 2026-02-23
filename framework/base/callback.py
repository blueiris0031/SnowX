from abc import ABC, abstractmethod
from dataclasses import fields
from inspect import iscoroutinefunction
from typing import Any, Type, TypeVar

from ..types.callback import (
    CallbackFunction,

    BaseArgs,
    BaseCallbackWrapperArgs,
    BaseCallbackExecutorArgs, CallbackItem,
)


T = TypeVar("T", bound=BaseArgs)


def _get_dataclass_keys(dataclass_type: Type[BaseArgs]) -> set[str]:
    return {field.name for field in fields(dataclass_type)}


def _convert_dataclass(dataclass_type: Type[T], kwargs: dict[str, Any]) -> T:
    raw_kwargs = {key: kwargs[key] for key in _get_dataclass_keys(dataclass_type) if key in kwargs}
    return dataclass_type(**raw_kwargs)


class BaseCallbackExecutor(ABC):
    def __init__(self, args_type: Type[BaseCallbackExecutorArgs]):
        self._args_type = args_type

    @property
    def args_type(self) -> Type[BaseCallbackExecutorArgs]:
        return self._args_type

    def __call__(self, cb_func: CallbackFunction, **kwargs) -> CallbackFunction:
        executor_args = _convert_dataclass(self.args_type, {"origin_func": cb_func, **kwargs})
        async def executor(*cb_args, **cb_kwargs) -> Any:
            return await self.executor(cb_func, executor_args, *cb_args, **cb_kwargs)

        return executor

    @abstractmethod
    async def executor(self, cb_func: CallbackFunction, executor_args: BaseCallbackExecutorArgs, *cb_args, **cb_kwargs) -> tuple[bool, Any | None]:
        if iscoroutinefunction(cb_func):
            return True, await cb_func(*cb_args, **cb_kwargs)

        return True, cb_func(*cb_args, **cb_kwargs)


class BaseCallbackWrapper(ABC):
    def __init__(self, args_type: Type[BaseCallbackWrapperArgs]):
        self._args_type = args_type

    @property
    def args_type(self) -> Type[BaseCallbackWrapperArgs]:
        return self._args_type

    def __call__(self, func: CallbackFunction, executor: BaseCallbackExecutor | None, **kwargs) -> CallbackFunction:
        if executor is not None:
            func = executor(func, origin_func=func, **kwargs)
        wrapper_args = _convert_dataclass(self.args_type, {"origin_func": func, **kwargs})
        async def wrapper(*cb_args, **cb_kwargs) -> Any:
            return await self.wrapper(func, wrapper_args, *cb_args, **cb_kwargs)

        return wrapper

    @abstractmethod
    async def wrapper(self, cb_func: CallbackFunction, wrapper_args: BaseCallbackWrapperArgs, *cb_args, **cb_kwargs) -> Any:
        pass


class BaseSchedulerItem(ABC):
    def __init__(self, cb_type: str, identifier: str, *callbacks: CallbackItem, **__):
        self._cb_type = cb_type
        self._identifier = identifier
        self._callbacks = callbacks

    @property
    def cb_type(self) -> str:
        return self._cb_type

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def callbacks(self) -> tuple[CallbackItem, ...]:
        return self._callbacks

    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self, force_stop: bool = False) -> None: ...


__all__ = [
    "BaseCallbackExecutor",
    "BaseCallbackWrapper",

    "BaseSchedulerItem",
]
