from functools import partial
from inspect import iscoroutinefunction
from typing import Any

from ...base.kernel.kernel import BaseKernelExtension
from ...types.kernel.basic_kernel import BasicKernelProtocol
from ...types.kernel.extensions.basic_kernel_interface import BasicKernelInterfaceExtensionProtocol


class BasicKernelInterfaceExtension(BaseKernelExtension, BasicKernelInterfaceExtensionProtocol):
    def __init__(self, basic_kernel: BasicKernelProtocol) -> None:
        super().__init__()

        self._basic_kernel = basic_kernel

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_") or iscoroutinefunction(attr := getattr(self._basic_kernel, name)): # Coroutine methods of BasicKernel must not be exposed outward.
            raise AttributeError(f"'BasicKernel' object has no attribute '{name}'")
        if not callable(attr):
            ret = attr
        else:
            ret = lambda *args, **kwargs: self.loop.call_soon_threadsafe(partial(attr, *args, **kwargs))
        setattr(self, name, ret)
        return ret

    def real_start(self) -> None:
        pass

    def real_stop(self, force: bool = False) -> None:
        pass


__all__ = [
    "BasicKernelInterfaceExtension",
]
