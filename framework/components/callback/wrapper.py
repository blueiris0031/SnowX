import asyncio
from typing import Any, Type

from ...base.callback import BaseCallbackExecutor, BaseCallbackWrapper
from ...kernel.event.bus import global_event_bus
from ...kernel.lock import global_async_completion_lock_manager
from ...kernel.logger import get_logger
from ...types.callback import BaseCallbackWrapperArgs, CallbackFunction
from ...types.callback import (
    BuiltinEmptyWrapperArgs,
    BuiltinProcessWrapperArgs,
    BuiltinAutorunWrapperArgs,
)
from ...types.event import BaseEvent


LOGGER = get_logger("CallbackWrapper")


class EmptyWrapper(BaseCallbackWrapper):
    def __init__(self):
        super().__init__(BuiltinEmptyWrapperArgs)

    async def wrapper(self, cb_func: CallbackFunction, wrapper_args: BaseCallbackWrapperArgs, *cb_args, **cb_kwargs) -> Any:
        return await cb_func(*cb_args, **cb_kwargs)


class ProcessWrapper(BaseCallbackWrapper):
    def __init__(self):
        super().__init__(BuiltinProcessWrapperArgs)

    def __call__(self, func: CallbackFunction, executor: BaseCallbackExecutor | None, **kwargs) -> CallbackFunction:
        if executor is None:
            raise ValueError("In <Process> type of wrapper, the executor parameter cannot be none")

        return super().__call__(func, executor, **kwargs)

    async def wrapper(self, cb_func: CallbackFunction, wrapper_args: BuiltinProcessWrapperArgs, *cb_args, **cb_kwargs) -> Type[BaseEvent] | None:
        if not cb_args and not cb_kwargs:
            return wrapper_args.event_type

        is_success, result = await cb_func(*cb_args, **cb_kwargs)
        if not is_success:
            return None

        await global_event_bus.auto_put(result)
        return None


class AutorunWrapper(BaseCallbackWrapper):
    def __init__(self):
        super().__init__(BuiltinAutorunWrapperArgs)

    def __call__(self, func: CallbackFunction, executor: BaseCallbackExecutor | None, **kwargs) -> CallbackFunction:
        if executor is None:
            raise ValueError("In <Autorun> type of wrapper, the executor parameter cannot be none")

        return super().__call__(func, executor, **kwargs)

    async def wrapper(self, cb_func: CallbackFunction, wrapper_args: BuiltinAutorunWrapperArgs, *_, **__) -> Any:
        lock = global_async_completion_lock_manager.get_lock(wrapper_args.origin_func)
        if wrapper_args.no_safe_exit:
            global_async_completion_lock_manager.set_nowait(wrapper_args.origin_func)

        while True:
            await wrapper_args.trigger.wait()

            async with lock:
                try:
                    is_success, result = await cb_func()
                    if is_success:
                        await global_event_bus.auto_put(result)
                except asyncio.CancelledError:
                    if wrapper_args.no_safe_exit:
                        LOGGER.info(f"[{wrapper_args.identifier}<{wrapper_args.func_name}>]: Exit <Autorun> callback function.")
                    else:
                        LOGGER.warning(f"[{wrapper_args.identifier}<{wrapper_args.func_name}>]: Unsafe exit <Autorun> callback function.")

                    raise asyncio.CancelledError


__all__ = [
    "EmptyWrapper",
    "ProcessWrapper",
    "AutorunWrapper",
]
