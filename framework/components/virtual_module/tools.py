from inspect import ismodule
from traceback import print_exc
from types import ModuleType
from typing import Any, Callable, TypeVar
from warnings import warn

from .module import VirtualModule


def _getter(getter: Callable[[object], str], obj: object, specified: str | None = None) -> Any:
    if specified and isinstance(specified, str):
        return specified
    if (getter_result := getter(obj)) and isinstance(getter_result, str):
        return getter_result
    return ""


def _default_name_getter(obj: object) -> str:
    return getattr(obj, "__name__", "")


_R = TypeVar("_R", bound=object)

def get_register_decorator(self: VirtualModule, name_getter: Callable[[object], str] | None = None) -> Callable[[_R | None, str | None], _R | Callable[[_R], _R]]:
    getter = name_getter or _default_name_getter
    def decorator(obj: _R | None, name: str | None = None) -> _R | Callable[[_R], _R]:
        def registrar(obj_: _R) -> _R:
            name_ = _getter(getter, obj_, name)
            if name_:
                self.register_object(name_, obj_)
            else:
                warn(f"Object {name_} not registered", RuntimeWarning)
            return obj_
        if obj is None:
            return registrar
        return registrar(obj)
    return decorator


def _get_exports(module: ModuleType) -> dict[str, Any]:
    if not isinstance(all_list := getattr(module, "__all__", None), (list, tuple)):
        return {}
    return {
        export_name: getattr(module, export_name)
        for export_name in all_list
        if isinstance(export_name, str)
        and not export_name.startswith("_")
        and hasattr(module, export_name)
    }

def register_module(self: VirtualModule, name: str, module: ModuleType, recursive: bool = False) -> None:
    register_stack: list[tuple[VirtualModule, str, ModuleType]] = [(self, name, module)]
    while register_stack:
        parent_v, current_n, current_m = register_stack.pop()
        if not ismodule(current_m) or not current_n or not isinstance(current_n, str):
            continue
        try:
            current_v = parent_v.get_sub_virtual_module(current_n)
        except Exception:
            warn(f"Module '{current_n}' registration abnormality, skip", RuntimeWarning)
            print_exc()
            continue

        for export_name, export in _get_exports(current_m).items():
            if recursive and isinstance(export, ModuleType):
                register_stack.append((current_v, export_name, export))
                continue
            try:
                current_v.register_object(export_name, export)
            except Exception:
                warn(f"Object '{export_name}' registration abnormality, skip", RuntimeWarning)
                print_exc()


__all__ = [
    "get_register_decorator",
    "register_module",
]
