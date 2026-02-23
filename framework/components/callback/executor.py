import asyncio
from typing import Any

from ...base.callback import BaseCallbackExecutor
from ...kernel.logger import get_logger
from ...types.callback import (
    CallbackFunction,

    BuiltinEmptyExecutorArgs,
    BuiltinExecutorArgs,
)


LOGGER = get_logger("CallbackExecutor")


class EmptyExecutor(BaseCallbackExecutor):
    def __init__(self):
        super().__init__(BuiltinEmptyExecutorArgs)

    async def executor(self, cb_func: CallbackFunction, executor_args: BuiltinEmptyExecutorArgs, *cb_args, **cb_kwargs) -> tuple[bool, Any | None]:
        return await super().executor(cb_func, executor_args, *cb_args, **cb_kwargs)


class BuiltinExecutor(BaseCallbackExecutor):
    """
    The default callback executor in the framework. Support timeout control and automatic retry of failure. \n
    Note: If the callback function is a synchronous function, the timeout parameter is not supported. \n
    param timeout: Callback execution timeout. If this parameter is 0, then do not set the timeout time. \n
    param retry_num: Callback retry number. If this parameter is 0, the callback function will not be retryd after the execution fails. \n
    param retry_interval: Callback retry interval. If this parameter is 0, it will be retryd immediately after the callback execution fails. \n
    """
    def __init__(self):
        super().__init__(BuiltinExecutorArgs)

    async def executor(self, cb_func: CallbackFunction, executor_args: BuiltinExecutorArgs, *cb_args, **cb_kwargs) -> tuple[bool, Any | None]:
        timeout = max(0, executor_args.timeout)
        retry_num = max(0, executor_args.retry_num)
        retry_interval = max(0, executor_args.retry_interval)

        for i in range(retry_num + 1):
            try:
                if timeout == 0:
                    return await super().executor(cb_func, executor_args, *cb_args, **cb_kwargs)
                else:
                    return await asyncio.wait_for(super().executor(cb_func, executor_args, *cb_args, **cb_kwargs), timeout=timeout)

            except asyncio.TimeoutError:
                LOGGER.warning(f"[{executor_args.identifier}<{executor_args.func_name}>]: Callback function runs out of time: ({timeout}s)")
            except asyncio.CancelledError:
                raise asyncio.CancelledError
            except Exception as e:
                LOGGER.error(f"[{executor_args.identifier}<{executor_args.func_name}>]: Callback function runs abnormally.", exc_info=e)

            if retry_num == 0:
                continue
            if i == retry_num:
                LOGGER.error(f"[{executor_args.identifier}<{executor_args.func_name}>]: The number of retrials has reached the upper limit: ({retry_num}/{retry_num})")
                continue

            await asyncio.sleep(retry_interval)
            LOGGER.warning(f"[{executor_args.identifier}<{executor_args.func_name}>]: Retrying({i + 1}/{retry_num})...")

        return False, None


__all__ = [
    "EmptyExecutor",
    "BuiltinExecutor",
]
