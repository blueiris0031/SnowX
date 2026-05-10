from abc import abstractmethod
from typing import LiteralString, Protocol, runtime_checkable, Mapping

from ..lifecycle import LifeCycleProtocol


@runtime_checkable
class KernelProtocol(LifeCycleProtocol, Protocol):
    @property
    @abstractmethod
    def loaded_extensions(self) -> Mapping[str, "KernelExtensionProtocol"]:
        pass

    @abstractmethod
    def __getattr__(self, extension_id: str) -> "KernelExtensionProtocol":
        pass

    @abstractmethod
    async def load_extension(self, extension: "KernelExtensionProtocol") -> None:
        pass

    @abstractmethod
    async def unload_extension(self, extension_id: str, force: bool = False) -> None:
        pass


@runtime_checkable
class KernelExtensionProtocol(LifeCycleProtocol, Protocol):
    @property
    @abstractmethod
    def identifier(self) -> LiteralString:
        pass

    @property
    @abstractmethod
    def dependencies(self) -> tuple[LiteralString, ...]:
        pass

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    def init(self, kernel: "KernelProtocol") -> None:
        """
        A hook used to inject functionality into the Kernel, will be triggered before loading. \n
        If an exception is raised, exit will be triggered automatically.
        """
        pass

    @abstractmethod
    def exit(self, kernel: "KernelProtocol") -> None:
        """
        A hook for cleaning up injected functionalities, will be triggered after unloading. \n
        Note: Exceptions raised by this hook will be ignored.
        """
        pass

    @abstractmethod
    async def stop(self, force: bool = False) -> None:
        """
        Note: Exceptions raised by this method will be ignored.
        """
        pass


__all__ = [
    "KernelProtocol",
    "KernelExtensionProtocol",
]
