import re
from sys import modules as sys_modules
from types import ModuleType
from typing import Callable, Optional

from ...error.virtual_module import ModuleExistsError, ObjectExistsError


_name_pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
def _name_checker(name: str) -> bool:
    return re.fullmatch(_name_pattern, name) is not None


class VirtualModule:
    _virtual_module_instance_map: dict[str, tuple["VirtualModule", bool]] = {}
    _object_registry: dict[str, tuple[object, bool]] = {}

    @staticmethod
    def _get_filter_func(full_name: str, is_module: bool) -> Callable[[tuple[str, tuple[object, bool]]], bool]:
        def filter_func(item: tuple[str, tuple[object, bool]]) -> bool:
            if not item[0].startswith(f"{full_name}."):
                return False
            return item[1][1] is is_module
        return filter_func

    @classmethod
    def _filter_registered(cls, full_name: str, is_module: bool) -> list[str]:
        return list(filter(cls._get_filter_func(full_name, is_module), cls._object_registry.items()))

    @classmethod
    def _cancel_registered_object(cls, full_name: str) -> None:
        for name, _ in cls._filter_registered(full_name, False):
            cls._object_registry.pop(name, None)

    @classmethod
    def _cancel_registered_sub_module(cls, full_name: str) -> None:
        for name, _ in cls._filter_registered(full_name, True):
            if name in cls._virtual_module_instance_map:
                cls._virtual_module_instance_map[name][0].cancel_virtual_module()
            cls._object_registry.pop(name, None)

    def __new__(cls, full_name: str) -> "VirtualModule":
        if full_name in cls._virtual_module_instance_map:
            return cls._virtual_module_instance_map[full_name][0]
        new_instance = super().__new__(cls)
        new_instance._is_available = True
        return cls._virtual_module_instance_map.setdefault(full_name, (new_instance, False))[0]

    def cancel_virtual_module(self):
        if not self._is_available:
            return
        self._is_available = False
        sys_modules.pop(self._full_name, None)
        self._cancel_registered_object(self._full_name)
        self._cancel_registered_sub_module(self._full_name)
        self._object_registry.pop(self._full_name, None)
        self._virtual_module_instance_map.pop(self._full_name, None)

    @property
    def is_available(self) -> bool:
        return self._is_available

    @staticmethod
    def _available_check_d(method: Callable) -> Callable:
        def wrapped(self: "VirtualModule", *args, **kwargs):
            if not self.is_available:
                raise RuntimeError(f"Virtual module '{self._full_name}' not available")
            return method(self, *args, **kwargs)
        return wrapped

    @_available_check_d
    def __init__(self, full_name: str) -> None:
        if self._virtual_module_instance_map[full_name][1]:
            return
        self.__real_init__(full_name)
        self._virtual_module_instance_map[full_name] = (self, True)

    @_available_check_d
    def __real_init__(self, full_name: str):
        if "." in full_name:
            parent_name, name = full_name.rsplit(".", 1)
        else:
            parent_name, name = None, full_name
        if not _name_checker(name):
            raise ValueError(f"Invalid Virtual module name: '{name}' in '{full_name}'")
        self._name, self._full_name = name, full_name
        self._init_module(parent_name)

    @_available_check_d
    def _module_getattr(self, name: str) -> object:
        full_name = f"{self._full_name}.{name}"
        if full_name not in self._object_registry:
            raise AttributeError(f"Object '{name}' does not exist")
        return self._object_registry[full_name][0]

    @_available_check_d
    def _init_module(self, parent_name: str | None) -> None:
        if self._full_name in self._object_registry:
            raise ObjectExistsError(f"'{self._full_name}' already exists")
        if parent_name is not None:
            self._parent = VirtualModule(parent_name)
        else:
            self._parent = None
        if self._full_name in sys_modules:
            raise ModuleExistsError(f"'{self._full_name}' already exists in 'sys.modules'")
        self._module = ModuleType(self._full_name)
        self._module.__path__ = []
        self._module.__getattr__ = self._module_getattr
        self._object_registry[self._full_name] = (self._module, True)
        sys_modules[self._full_name] = self._module

    @property
    @_available_check_d
    def name(self) -> str:
        return self._name

    @property
    @_available_check_d
    def full_name(self) -> str:
        return self._full_name

    @property
    @_available_check_d
    def module(self) -> ModuleType:
        return self._module

    @property
    @_available_check_d
    def parent(self) -> Optional["VirtualModule"]:
        return self._parent

    @_available_check_d
    def get_sub_virtual_module(self, name: str) -> "VirtualModule":
        return VirtualModule(f"{self._full_name}.{name}")

    @_available_check_d
    def register_object(self, name: str, obj: object) -> None:
        if not _name_checker(name):
            raise ValueError(f"Invalid object name: '{name}'")
        full_name = f"{self._full_name}.{name}"
        if full_name in self._object_registry:
            raise ObjectExistsError(f"Object '{name}' already exists")
        self._object_registry[full_name] = (obj, False)

    @_available_check_d
    def cancel_object(self, name: str) -> None:
        full_name = f"{self._full_name}.{name}"
        if full_name not in self._object_registry:
            return
        if self._object_registry[full_name][1]:
            return
        self._object_registry.pop(full_name, None)


__all__ = [
    "VirtualModule",
]
