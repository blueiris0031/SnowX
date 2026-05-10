import asyncio
import importlib
import sys
import traceback
from code import InteractiveConsole
from shutil import get_terminal_size
from typing import Callable, Coroutine, ParamSpec, TypeVar
from uuid import uuid4

from ...base.kernel import BaseKernelExtension
from ...constants.logger import ROOT_NAME
from ...mixins.loggable import LoggableMixin
from ...types.kernel import KernelProtocol
from ...utils.void import VoidClass, AWAITABLE_TEMPLATE


class _Void(VoidClass, **AWAITABLE_TEMPLATE):
    """
    VoidTask
    """
    pass


_P = ParamSpec("_P")
_R = TypeVar("_R", bound=object)


class InteractiveConsoleExtension(BaseKernelExtension, LoggableMixin):
    @property
    def identifier(self) -> str:
        return "interact"

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ()

    def __init__(self):
        super().__init__()

        self._interact_task: asyncio.Task | _Void = _Void()
        self._kernel_pointer: KernelProtocol | None = None

        self.set_logger(f"{ROOT_NAME}.interact")

    def _console(self) -> None:
        exit_key = uuid4().hex
        def quit_and_exit() -> None:
            print("Exiting interactive console...")
            raise SystemExit(exit_key)

        def dispatch(
                func: Callable[_P, Coroutine[None, None, _R]],
                /,
                *args: _P.args,
                **kwargs: _P.kwargs,
        ) -> _R:
            try:
                return self._kernel_pointer.dispatcher.dispatch(func, *args, **kwargs)
            except AttributeError:
                raise RuntimeError("'DispatcherExtension' not loaded, this function cannot be used")

        interact_locals = {
            "kernel": self._kernel_pointer,

            "asyncio": asyncio,
            "importlib": importlib,
            "traceback": traceback,

            "dispatch": dispatch,
            "exit": quit_and_exit,
            "reload_module": importlib.reload,
            "quit": quit_and_exit,
        }

        cprt = (
                'Type "help", "copyright", "credits" or "license" for more information.\n\n' +
                ("-" * (get_terminal_size().columns // 2)) + '\n' +
                'You have entered the interactive console of the framework.\n' +
                ("-" * (get_terminal_size().columns // 2))
        )

        try:
            import readline
        except ImportError:
            pass

        console = InteractiveConsole(locals=interact_locals, filename="<snowx_console>")
        try:
            console.interact(banner=f"Python {sys.version} on {sys.platform}\n{cprt}\n")
        except SystemExit as exc:
            if not (exc_args := exc.args):
                raise
            if exc_args[0] != exit_key:
                raise

    def init(self, kernel: KernelProtocol) -> None:
        self._kernel_pointer = kernel

    async def real_start(self) -> None:
        console_coro = asyncio.to_thread(self._console)
        self._interact_task = asyncio.create_task(console_coro)
        self.logger.info("Console start successfully.")

    async def real_stop(self, force: bool = False) -> None:
        self.logger.warning("If console is still running, use 'quit()' or 'exit()' to exit.")
        if force:
            self._interact_task.cancel()
        try:
            await self._interact_task
        except asyncio.CancelledError:
            pass
        self._interact_task = _Void()

    def exit(self, kernel: KernelProtocol) -> None:
        self._kernel_pointer = None


__all__ = [
    "InteractiveConsoleExtension",
]
