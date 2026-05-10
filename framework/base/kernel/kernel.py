from abc import ABC
from typing import cast

from ..lifecycle import BaseLifeCycle
from ...types.kernel.kernel import KernelProtocol, KernelExtensionProtocol


class BaseKernelExtension(BaseLifeCycle, KernelExtensionProtocol, ABC):
    _kernel_ptr: KernelProtocol | None = None

    @property
    def kernel(self) -> KernelProtocol:
        return cast(KernelProtocol, self._kernel_ptr)

    def init(self, kernel: KernelProtocol) -> None:
        """
        This method saves a reference to the kernel by default. Override it for extended features. \n
        If you need this reference after overriding, call 'super().init(kernel)' first in the function body.
        """
        self._kernel_ptr = kernel

    def exit(self, kernel: KernelProtocol) -> None:
        """
        This method sets the kernel reference to None by default. Override it for extended features. \n
        Place 'super().exit(kernel)' at the end of your overridden function.
        """
        self._kernel_ptr = None


__all__ = [
    "BaseKernelExtension",
]
