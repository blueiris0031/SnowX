from argparse import ArgumentParser
from typing import Literal, cast

from ...base.kernel.kernel import BaseKernelExtension
from ...error.kernel import StopSignal
from ...types.kernel.extensions.basic_kernel_interface import BasicKernelInterfaceExtensionProtocol
from ...types.kernel.kernel import KernelProtocol
from ...utils.singleton import singleton_decorator


@singleton_decorator
class InitExtension(BaseKernelExtension):
    @property
    def identifier(self) -> Literal["init"]:
        return "init"

    @property
    def dependencies(self) -> tuple[Literal["basic_kernel_interface"]]:
        return ("basic_kernel_interface", )

    def __init__(self):
        super().__init__()

        self._parser = ArgumentParser()
        self._parser.add_argument(
            "-i", "--interact",
            action="store_true",
            dest="interact",
            help="interactive mode",
        )
        self._parser.add_argument(
            "--level",
            action="store",
            default=-1,
            dest="level",
            help="init level (default: %(default)s)",
            type=int,
        )

    def init(self, kernel: KernelProtocol) -> None:
        task_interface = cast(BasicKernelInterfaceExtensionProtocol, kernel.basic_kernel_interface).submit_task
        try:
            args = self._parser.parse_args()
        except SystemExit:
            def stop() -> None: raise StopSignal
            task_interface(stop)
            return

        from .sub_init import SubInitExtension
        sub_init_extension = SubInitExtension(args.level)
        async def load_sub_init_extension() -> None: await kernel.load_extension(sub_init_extension)
        task_interface(load_sub_init_extension, True)

        if not args.interact:
            return
        from .interact import InteractiveConsoleExtension
        interactive_extension = InteractiveConsoleExtension()
        async def load_interactive_extension() -> None: await kernel.load_extension(interactive_extension)
        task_interface(load_interactive_extension)

    def real_start(self) -> None:
        pass

    def real_stop(self, force: bool = False) -> None:
        pass


__all__ = [
    "InitExtension",
]
