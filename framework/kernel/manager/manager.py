from typing import Any, Awaitable, Callable

from ..logger import get_logger
from ...components.callback.executor import BuiltinExecutor
from ...state.framework import (
    set_started,
    set_stopping,
)


LOGGER = get_logger("FrameworkManager")


class FrameworkManager:
    def __init__(self):
        self._framework_start_sign: bool = False

        self._start_func: list[Callable[[], Awaitable[tuple[bool, Any]]]] = []
        self._stop_func: list[Callable[[bool], Awaitable[tuple[bool, Any]]]] = []

        self._executor = BuiltinExecutor()

    @property
    def start_func(self) -> tuple[Callable[[], Awaitable[tuple[bool, Any]]], ...]:
        return tuple(self._start_func)

    @property
    def stop_func(self) -> tuple[Callable[[bool], Awaitable[tuple[bool, Any]]], ...]:
        return tuple(self._stop_func)

    @property
    def executor(self) -> BuiltinExecutor:
        return self._executor

    def _wrap_func(self, func: Callable[..., Awaitable[Any] | Any]) -> Callable[..., Awaitable[tuple[bool, Any]]]:
        return self.executor(
            func,
            identifier="framework_manager",
            func_name=getattr(func, "__name__", "UnknownFunction"),
        )

    def inject_start_func(self, func: Callable[[], Awaitable[Any] | Any]) -> None:
        self._start_func.append(self._wrap_func(func))

    def inject_stop_func(self, func: Callable[[bool], Awaitable[Any] | Any]) -> None:
        self._stop_func.append(self._wrap_func(func))

    async def start(self) -> None:
        if self._framework_start_sign:
            return

        self._framework_start_sign = True
        for func in self._start_func:
            is_success, _ = await func()
            if not is_success:
                LOGGER.error("Framework start failed.")
                set_stopping()
                return

        set_started()
        LOGGER.info("Framework started.")

    async def stop(self, force: bool) -> None:
        if not self._framework_start_sign:
            return

        self._framework_start_sign = False
        set_stopping()
        for func in self._stop_func:
            await func(force)

        LOGGER.info("Framework stopped.")


framework_manager = FrameworkManager()


__all__ = [
    "framework_manager",
]
