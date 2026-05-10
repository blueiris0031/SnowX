from abc import abstractmethod
from typing import Any, Literal, Protocol, runtime_checkable

from ..kernel import KernelExtensionProtocol


@runtime_checkable
class BasicKernelInterfaceExtensionProtocol(KernelExtensionProtocol, Protocol):
    @property
    def identifier(self) -> Literal["basic_kernel_interface"]:
        return "basic_kernel_interface"

    @property
    def dependencies(self) -> tuple[()]:
        return ()

    @abstractmethod
    def __getattr__(self, name: str) -> Any:
        pass


__all__ = [
    "BasicKernelInterfaceExtensionProtocol",
]
