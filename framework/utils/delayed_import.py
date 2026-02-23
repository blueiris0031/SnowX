from importlib import import_module
from types import ModuleType
from typing import Callable


def delayed_import(all_: list[str], package: str) -> Callable[[str], ModuleType]:
    def getattr_(name: str) -> ModuleType:
        if name in all_:
            return import_module(name, package)
        raise AttributeError(f"module {package} has no attribute {name}")
    return getattr_


__all__ = [
    "delayed_import",
]
