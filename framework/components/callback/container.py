from itertools import chain
from typing import Callable

from ...types.callback import CallbackItem


class IDLevelContainer:
    def __init__(self, identifier: str) -> None:
        self._identifier = identifier

        self._callback_item_map: dict[Callable, CallbackItem] = {}

    @property
    def identifier(self) -> str:
        return self._identifier

    def get(self) -> tuple[CallbackItem, ...]:
        return tuple(self._callback_item_map.values())

    def add(self, callback_item: CallbackItem) -> None:
        if not isinstance(callback_item, CallbackItem):
            raise TypeError("callback_item must be of type CallbackItem")
        self._callback_item_map.setdefault(callback_item.func, callback_item)

    def clear(self) -> None:
        self._callback_item_map.clear()

    def __del__(self) -> None:
        self.clear()


class TypeLevelContainer:
    def __init__(self, callback_type: str) -> None:
        self._callback_type = callback_type

        self._id_container_map: dict[str, IDLevelContainer] = {}

    @property
    def callback_type(self) -> str:
        return self._callback_type

    def get(self, identifier: str) -> IDLevelContainer:
        return self._id_container_map.setdefault(identifier, IDLevelContainer(identifier))

    def get_all(self) -> tuple[IDLevelContainer, ...]:
        return tuple(self._id_container_map.values())

    def auto_get(self, identifier: str | None) -> tuple[CallbackItem, ...]:
        return tuple(
            chain(
                *(
                    container.get()
                    for container in (
                        self.get_all()
                        if identifier is None
                        else (self.get(identifier), )
                    )
                )
            )
        )

    def add(self, identifier: str) -> None:
        self.get(identifier)

    def auto_add(self, callback_item: CallbackItem) -> None:
        if not isinstance(callback_item, CallbackItem):
            raise TypeError("callback_item must be of type CallbackItem")
        self.get(callback_item.identifier).add(callback_item)

    def remove(self, identifier: str) -> None:
        self._id_container_map.pop(identifier, None)

    def clear(self) -> None:
        self._id_container_map.clear()

    def __del__(self) -> None:
        self.clear()


class CallbackContainer:
    def __init__(self) -> None:
        self._type_container_map: dict[str, TypeLevelContainer] = {}

    def get(self, callback_type: str) -> TypeLevelContainer:
        return self._type_container_map.setdefault(callback_type, TypeLevelContainer(callback_type))

    def get_all(self) -> tuple[TypeLevelContainer, ...]:
        return tuple(self._type_container_map.values())

    def auto_get(self, callback_type: str | None = None, identifier: str | None = None) -> tuple[CallbackItem, ...]:
        return tuple(
            chain(
                *(
                    t_container.auto_get(identifier)
                    for t_container in (
                        self.get_all()
                        if callback_type is None
                        else (self.get(callback_type), )
                    )
                )
            )
        )

    def add(self, callback_type: str) -> None:
        self.get(callback_type)

    def auto_add(self, callback_item: CallbackItem) -> None:
        if not isinstance(callback_item, CallbackItem):
            raise TypeError("callback_item must be of type CallbackItem")
        self.get(callback_item.type).auto_add(callback_item)

    def remove(self, callback_type: str) -> None:
        self._type_container_map.pop(callback_type, None)

    def auto_remove(self, identifier: str, callback_type: str | None = None) -> None:
        for t_container in (
            self.get_all() if callback_type is None
            else (self.get(callback_type), )
        ):
            t_container.remove(identifier)

    def clear(self) -> None:
        self._type_container_map.clear()

    def __del__(self) -> None:
        self.clear()


__all__ = [
    "CallbackContainer"
]
