from inspect import ismodule
from types import ModuleType
from typing import Any, Callable

from .constants import VMODULE_ROOT_PATH, VMODULE_SUBROOT_PATH
from .manager import global_vmodule_manager
from .utils import get_all_export


class Adder:
    def __init__(self, parent_path: str) -> None:
        self._parent_path = parent_path

        self.add_class = self.add_function # The logic is the same, and the name is different.

    def get_sub_adder(self, name: str) -> "Adder":
        return Adder(f"{self._parent_path}.{name}")

    def add_object(self, name: str, obj: Any) -> bool:
        return global_vmodule_manager.add_object(f"{self._parent_path}.{name}", obj)

    @staticmethod
    def _get_func_name(name: str, func: Callable[..., Any]) -> str:
        if name:
            return name
        if not hasattr(func, "__name__"):
            return ""
        return func.__name__

    def add_function(self, name: str | Callable[..., Any] | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]] | Callable[..., Any]:
        def adder(func: Callable[..., Any]) -> Callable[..., Any]:
            func_name = self._get_func_name(name, func)
            if not func_name:
                return func
            self.add_object(func_name, func)
            return func

        if callable(name):
            be_decorated, name = name, None
            return adder(be_decorated)
        return adder

    def _auto_add(self, module: ModuleType, add_module: bool = True) -> dict[str, Any]:
        exports = get_all_export(module)
        for name, obj in exports.items():
            if isinstance(obj, ModuleType) and not add_module:
                continue
            self.add_object(name, obj)

        return exports

    def _recursive_auto_add(self, module: ModuleType) -> dict[str, Any]:
        full_exports: dict[str, Any] = {}

        module_stack: list[tuple["Adder", ModuleType, dict[str, Any]]] = [(self, module, full_exports)]
        while module_stack:
            adder, current_module, exports = module_stack.pop()
            current_exports = adder._auto_add(current_module, add_module=False)
            exports.update(current_exports)

            for name, obj in current_exports.items():
                if not ismodule(obj):
                    continue
                if not hasattr(obj, "__name__") or not hasattr(current_module, "__name__"):
                    continue

                obj_name = getattr(obj, "__name__")
                current_name = getattr(current_module, "__name__")
                if not isinstance(obj_name, str) or not isinstance(current_name, str):
                    continue
                if "." not in obj_name:
                    continue

                parent, name = getattr(obj, "__name__").rsplit(".", maxsplit=1)
                if parent != current_name:
                    continue

                exports[name]: dict[str, Any] = {}
                module_stack.append((adder.get_sub_adder(name), obj, exports[name]))

        return full_exports

    def auto_add(self, module: ModuleType, recursive: bool = False) -> dict[str, Any]:
        if recursive:
            return self._recursive_auto_add(module)
        else:
            return self._auto_add(module, add_module=True)


PLUGINS_ROOT_PATH = f"{VMODULE_ROOT_PATH.ROOT}.{VMODULE_SUBROOT_PATH.PLUGINS}"
_plugin_adder = Adder(PLUGINS_ROOT_PATH)

def add_plugin(plugin_id: str, plugin_module: ModuleType) -> None:
    sub_adder = _plugin_adder.get_sub_adder(plugin_id)
    sub_adder.auto_add(plugin_module, recursive=True)

def get_plugin(plugin_id: str) -> ModuleType | None:
    return global_vmodule_manager.get_vmodule(f"{PLUGINS_ROOT_PATH}.{plugin_id}")

def del_plugin(plugin_id: str) -> None:
    global_vmodule_manager.del_vmodule(f"{PLUGINS_ROOT_PATH}.{plugin_id}")


__all__ = [
    "Adder",
    "add_plugin",
    "get_plugin",
    "del_plugin",
]
