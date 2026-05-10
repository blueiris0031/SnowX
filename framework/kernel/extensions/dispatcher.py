from asyncio import get_running_loop, wrap_future
from concurrent.futures import InvalidStateError, Future as ThreadFuture
from inspect import iscoroutinefunction
from typing import Callable, Coroutine, ParamSpec, Self, TypeVar, cast

from ...base.kernel import BaseKernelExtension
from ...base.lifecycle import with_running_check
from ...types.kernel import KernelProtocol


_TASK_INTERFACE = Callable[[Callable[[], Coroutine[None, None, None] | None], bool], None]
_P = ParamSpec("_P")
_R = TypeVar("_R")


class DispatcherExtension(BaseKernelExtension):
    @property
    def identifier(self) -> str:
        return "dispatcher"

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ("base_kernel_interface", )

    def __init__(self):
        super().__init__()

        self._task_interface: _TASK_INTERFACE | None = None

    def init(self, kernel: KernelProtocol) -> None:
        self._task_interface = kernel.base_kernel_interface.submit_task

    def real_start(self) -> None:
        pass

    def real_stop(self, force: bool = False) -> None:
        pass

    def exit(self, kernel: KernelProtocol) -> None:
        self._task_interface = None

    def _submit_dispatch(
            self,
            func: Callable[_P, Coroutine[None, None, _R] | _R],
            /,
            *args: _P.args,
            **kwargs: _P.kwargs,
    ) -> ThreadFuture[_R]:
        fut = ThreadFuture()
        def ret_call(method: Callable[[_R], None], ret: _R) -> None:
            try: method(ret)
            except InvalidStateError: pass

        if iscoroutinefunction(func):
            async def task() -> None:
                try: ret_call(fut.set_result, await func(*args, **kwargs))
                except BaseException as e:
                    ret_call(fut.set_exception, e)
                    raise
        else:
            def task() -> None:
                try: ret_call(fut.set_result, func(*args, **kwargs))
                except BaseException as e:
                    ret_call(fut.set_exception, e)
                    raise

        cast(_TASK_INTERFACE, self._task_interface)(task, False)
        return fut

    @with_running_check(True)
    def dispatch(
            self: Self,
            func: Callable[_P, Coroutine[None, None, _R] | _R],
            /,
            *args: _P.args,
            **kwargs: _P.kwargs,
    ) -> _R:
        """
        Not supported on the main thread.
        """
        try:
            loop = get_running_loop()
        except RuntimeError:
            loop = None
        if self.loop is loop:
            raise RuntimeError("'dispatch' is not supported on the main thread")
        fut = self._submit_dispatch(func, *args, **kwargs)
        return fut.result()

    @with_running_check(True)
    async def async_dispatch(
            self: Self,
            func: Callable[_P, Coroutine[None, None, _R] | _R],
            /,
            *args: _P.args,
            **kwargs: _P.kwargs,
    ) -> _R:
        fut = self._submit_dispatch(func, *args, **kwargs)
        return await wrap_future(fut, loop=get_running_loop())


__all__ = [
    "DispatcherExtension",
]
