from types import ModuleType
from typing import Any

from .utils import (
    path_checker,
    new_vmodule,
    add_module,
    get_module,
    del_module,
)


class VModuleManager:
    def __init__(self):
        self._vmodule_records: set[str] = set()
        self._object_records: set[str] = set()

    def _add_vmodule(self, full_path: str) -> bool:
        if not path_checker(full_path):
            return False
        if full_path in self._vmodule_records:
            return True
        vmodule = new_vmodule(full_path)
        if not add_module(full_path, vmodule):
            return False
        self._vmodule_records.add(full_path)
        return True

    def _get_vmodule(self, full_path: str) -> ModuleType | None:
        if full_path not in self._vmodule_records:
            return None
        return get_module(full_path)

    def _del_vmodule(self, full_path: str) -> None:
        if full_path not in self._vmodule_records:
            return
        self._vmodule_records.remove(full_path)
        del_module(full_path)

    def add_vmodule(self, full_path: str) -> bool:
        if not path_checker(full_path):
            return False

        split_list = full_path.split(".")
        added_list: set[str] = set()
        for index in range(len(split_list)):
            current_path = ".".join(split_list[:index+1])
            if current_path in self._vmodule_records:
                continue
            if not self._add_vmodule(current_path):
                break

            added_list.add(current_path)
            if index == 0:
                continue

            parent_vmodule = self._get_vmodule(current_path.rsplit(".", 1)[0])
            current_vmodule = self._get_vmodule(current_path)
            setattr(parent_vmodule, split_list[index], current_vmodule)

        else:
            return True

        for added_path in added_list:
            self._del_vmodule(added_path)
        return False

    def get_vmodule(self, full_path: str) -> ModuleType | None:
        return self._get_vmodule(full_path)

    def del_vmodule(self, full_path: str) -> None:
        del_list: set[str] = set()
        for added_obj in self._object_records:
            if added_obj.startswith(f"{full_path}."):
                del_list.add(added_obj)
        for del_path in del_list:
            self.del_object(del_path)

        del_list.clear()
        del_list.add(full_path)
        for added_path in self._vmodule_records:
            if added_path.startswith(f"{full_path}."):
                del_list.add(added_path)
        for del_path in del_list:
            self._del_vmodule(del_path)

    def add_object(self, full_path: str, obj: Any) -> bool:
        if not path_checker(full_path):
            return False
        if full_path in self._object_records:
            return True

        parent_path, name = full_path.rsplit(".", 1)
        if not self.add_vmodule(parent_path):
            return False
        vmodule = self.get_vmodule(parent_path)
        setattr(vmodule, name, obj)
        self._object_records.add(full_path)
        return True

    def get_object(self, full_path: str) -> Any | None:
        if full_path not in self._object_records:
            return None

        parent_path, name = full_path.rsplit(".", 1)
        return getattr(self.get_vmodule(parent_path), name, None)

    def del_object(self, full_path: str) -> None:
        if full_path not in self._object_records:
            return

        parent_path, name = full_path.rsplit(".", 1)
        try:
            delattr(self.get_vmodule(parent_path), name)
        except AttributeError:
            pass
        self._object_records.remove(full_path)

global_vmodule_manager = VModuleManager()


__all__ = [
    "global_vmodule_manager",
]
