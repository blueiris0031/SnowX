import re
from inspect import ismodule
from sys import modules as sys_modules
from types import ModuleType
from typing import Any


_path_pattern = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")

def path_checker(path: str) -> bool:
    return all(re.fullmatch(_path_pattern, split) is not None for split in path.split("."))


def new_vmodule(full_path: str) -> ModuleType:
    vmodule = ModuleType(full_path)
    vmodule.__path__ = []
    return vmodule


def add_module(full_path: str, module: ModuleType) -> bool:
    if full_path in sys_modules:
        return False
    sys_modules[full_path] = module
    return True

def get_module(full_path: str) -> ModuleType | None:
    module = sys_modules.get(full_path, None)
    if ismodule(module):
        return module
    return None

def del_module(full_path: str) -> None:
    sys_modules.pop(full_path, None)


def get_all_export(module: ModuleType) -> dict[str, Any]:
    if not hasattr(module, "__all__"):
        return {}

    try:
        all_list = list(getattr(module, "__all__"))
    except TypeError:
        return {}

    export = {}
    for name in all_list:
        if not hasattr(module, name):
            continue
        export[name] = getattr(module, name)

    return export


__all__ = [
    "path_checker",
    "new_vmodule",
    "add_module",
    "get_module",
    "del_module",
    "get_all_export",
]