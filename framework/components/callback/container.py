from typing import Callable

from ...types.callback import CallbackItem


class PluginLevelContainer:
    def __init__(self, plugin_id: str) -> None:
        self.plugin_id = plugin_id

        self._callbacks: dict[Callable, CallbackItem] = {}

    def get(self) -> tuple[CallbackItem, ...]:
        return tuple[CallbackItem, ...](self._callbacks.values())

    def add(self, callback: CallbackItem) -> None:
        if callback.origin_func in self._callbacks:
            return

        self._callbacks[callback.origin_func] = callback


class TypeLevelContainer:
    def __init__(self, cb_type: str) -> None:
        self.cb_type = cb_type

        self._plugin_level_containers: dict[str, PluginLevelContainer] = {}

    def get(self, plugin_id: str) -> tuple[CallbackItem, ...]:
        result: list[CallbackItem] = []
        if plugin_id not in self._plugin_level_containers:
            return ()

        result.extend(self._plugin_level_containers[plugin_id].get())
        return tuple(result)

    def get_plugin_id(self) -> tuple[str, ...]:
        return tuple(self._plugin_level_containers.keys())

    def add(self, plugin_id: str, callback: CallbackItem) -> None:
        self._plugin_level_containers.setdefault(plugin_id, PluginLevelContainer(plugin_id)).add(callback)

    def remove(self, plugin_id: str) -> None:
        self._plugin_level_containers.pop(plugin_id, None)


class CallbackContainer:
    def __init__(self) -> None:
        self._type_level_containers: dict[str, TypeLevelContainer] = {}

    def get(self, cb_type: str, plugin_id: str) -> tuple[CallbackItem, ...]:
        if cb_type not in self._type_level_containers:
            return ()

        return self._type_level_containers[cb_type].get(plugin_id)

    def get_plugin_id(self, cb_type: str) -> tuple[str, ...]:
        if cb_type not in self._type_level_containers:
            return ()

        return self._type_level_containers[cb_type].get_plugin_id()

    def add(self, plugin_id: str, func_name: str, cb_type: str, raw_func: Callable, cb_func: Callable) -> None:
        container = self._type_level_containers.setdefault(cb_type, TypeLevelContainer(cb_type))
        container.add(plugin_id, CallbackItem(plugin_id, func_name, cb_type, raw_func, cb_func))

    def remove(self, cb_type: str, plugin_id: str) -> None:
        if cb_type not in self._type_level_containers:
            return

        self._type_level_containers[cb_type].remove(plugin_id)

    def remove_from_plugin_id(self, plugin_id: str) -> None:
        for container in self._type_level_containers.values():
            container.remove(plugin_id)


__all__ = [
    "CallbackContainer"
]
