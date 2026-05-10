from ...base.kernel import AbstractKernelExtension
from ...base.lifecycle import BaseLifeCycle
from ...components.virtual_module.engine import VirtualModule
from ...components.virtual_module.tools import inject_register_decorator, inject_register_module
from ...constants.virtual_module import ModulePath


class VirtualModuleExtension(BaseLifeCycle, AbstractKernelExtension):
    @property
    def identifier(self) -> str:
        return "virtual_module"

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ()

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get_virtual_module(type_: ModulePath) -> VirtualModule:
        if not isinstance(type_, ModulePath):
            raise TypeError(f"Unsupported builtin virtual module type '{type_}'")
        virtual_module = VirtualModule(type_)
        try:
            inject_register_decorator(virtual_module)
        except AttributeError:
            pass
        try:
            inject_register_module(virtual_module)
        except AttributeError:
            pass
        return virtual_module

    def real_start(self) -> None:
        pass

    def real_stop(self, force: bool = False) -> None:
        pass


__all__ = [
    "VirtualModuleExtension",
]
