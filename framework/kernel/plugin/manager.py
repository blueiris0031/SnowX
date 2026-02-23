from types import MappingProxyType
from typing import Awaitable, Callable, Any, Mapping, Iterable

from .deps import (
    get_deps_table_from_info,
    get_deps_table_from_item,
    topo_sort,
    get_ldeps_plugin,
    get_rdeps_plugin,
)
from .info import get_all_plugin_info
from ..logger import get_logger
from ...components.callback.executor import BuiltinExecutor
from ...types.plugin import Info, Item


LOGGER = get_logger("PluginManager")


class PluginManager:
    def __init__(self):
        self._load_order: list[
            tuple[
                Callable[[str], Awaitable[bool]],
                Callable[[str, bool], Awaitable[None]],
            ]
        ] = []

        self._plugin_infos: dict[str, Info] = {}
        self._loaded_plugins: dict[str, Item] = {}
        self._executor = BuiltinExecutor()

        self.update_plugin_infos()

    @property
    def load_order(self) -> tuple[
        tuple[
            Callable[[str], Awaitable[bool]],
            Callable[[str, bool], Awaitable[None]],
        ], ...
    ]:
        return tuple(self._load_order)

    @property
    def plugin_infos(self) -> MappingProxyType[str, Info]:
        return MappingProxyType(self._plugin_infos)

    @property
    def loaded_plugins(self) -> MappingProxyType[str, Item]:
        return MappingProxyType(self._loaded_plugins)

    @property
    def info_deps_table(self) -> dict[str, tuple[str, ...]]:
        return get_deps_table_from_info(self.plugin_infos.values())

    @property
    def loaded_deps_table(self) -> dict[str, tuple[str, ...]]:
        return get_deps_table_from_item(self.loaded_plugins.values())

    @property
    def executor(self) -> BuiltinExecutor:
        return self._executor

    def update_plugin_infos(self) -> None:
        self._plugin_infos = {info.metadata.id: info for info in get_all_plugin_info()}

    def _wrap_func(self, func: Callable[..., Awaitable[...] | ...]) -> Callable[..., Awaitable[...]]:
        executor_wrapped = self.executor(
            func,
            identifier="plugin_manager",
            func_name=getattr(func, "__name__", "UnknownFunction"),
        )
        async def wrapper(*args, **kwargs) -> Any:
            return await executor_wrapped(self, *args, **kwargs)

        return wrapper

    def inject_load_func(
            self,
            load_func: Callable[["PluginManager", str], Awaitable[bool | Item]],
            unload_func: Callable[["PluginManager", str, bool], Awaitable[None]],
    ) -> None:
        """
        Inject functions in order.
        :param load_func: Loading function
        :param unload_func: Corresponding unloading function
        :return: None
        """
        self._load_order.append(
            (
                self._wrap_func(load_func),
                self._wrap_func(unload_func),
            )
        )

    async def _single_load(self, identifier: str) -> bool:
        if identifier in self.loaded_plugins:
            return True

        for index in range(len(self.load_order)):
            load_func, _ = self.load_order[index]
            is_success, load_result = await load_func(identifier)
            if is_success:
                if isinstance(load_result, Item):
                    self._loaded_plugins[identifier] = load_result
                    continue
                if load_result:
                    continue

            while index >= 0:
                _, unload_func = self.load_order[index]
                await unload_func(identifier, False)
                index -= 1

            self._loaded_plugins.pop(identifier, None)
            return False

        return True

    async def _batch_load(
            self,
            load_list: Iterable[str],
            deps_table: Mapping[str, tuple[str, ...]],
    ) -> tuple[str, ...]:
        failed_list: set[str] = set()

        load_list = list(load_list)
        while load_list:
            id_ = load_list.pop()
            LOGGER.info(f"Prepare to load <{id_}> ...")
            if await self._single_load(id_):
                LOGGER.info(f"Successfully loaded <{id_}> .")
                continue

            LOGGER.error(f"Failed to load <{id_}> .")
            failed_list.add(id_)
            remove_list, _ = get_rdeps_plugin(id_, deps_table)
            for remove_id in remove_list:
                failed_list.add(remove_id)
                try:
                    load_list.remove(remove_id)
                except ValueError:
                    pass

        return tuple(failed_list)

    async def load_single(self, identifier: str) -> bool:
        if identifier in self.loaded_plugins:
            return True
        if identifier not in self.plugin_infos:
            return False

        deps_table = self.info_deps_table
        load_list, circ_list = get_ldeps_plugin(identifier, deps_table)
        if circ_list:
            for circ_id in circ_list:
                LOGGER.warning(f"Due to loop dependence, <{circ_id}> will not be loaded.")
            LOGGER.error(f"Failed to load <{identifier}> .")
            return False

        failed_list = await self._batch_load(load_list, deps_table)
        if not failed_list:
            return True
        for failed_id in failed_list:
            LOGGER.warning(f"Plugin <{failed_id}> not loaded.")
        LOGGER.error(f"Failed to load <{identifier}> .")
        return False

    async def load_all(self) -> None:
        deps_table = self.info_deps_table
        load_list, circ_list = topo_sort(deps_table)
        if circ_list:
            for circ_id in circ_list:
                LOGGER.warning(f"Due to loop dependence, <{circ_id}> will not be loaded.")

        failed_list = await self._batch_load(load_list, deps_table)
        for failed_id in failed_list:
            LOGGER.warning(f"Plugin <{failed_id}> not loaded.")

    async def _single_unload(self, identifier: str, force: bool) -> None:
        if identifier not in self.loaded_plugins:
            return
        for _, unload_func in self.load_order[::-1]:
            await unload_func(identifier, force)
        self._loaded_plugins.pop(identifier, None)

    async def _batch_unload(self, unload_list: Iterable[str], force: bool) -> None:
        unload_list = list(unload_list)
        while unload_list:
            id_ = unload_list.pop()
            LOGGER.info(f"Prepare to unload <{id_}> ...")
            await self._single_unload(id_, force)
            LOGGER.info(f"Successfully unload <{id_}> .")

    async def unload_single(self, identifier: str, force: bool = False) -> None:
        if identifier not in self.loaded_plugins:
            return

        unload_list, _ = get_rdeps_plugin(identifier, self.loaded_deps_table)
        await self._batch_unload(unload_list, force)

    async def unload_all(self, force: bool = False) -> None:
        unload_list, _ = topo_sort(self.loaded_deps_table)
        await self._batch_unload(unload_list[::-1], force)

    async def reload_single(self, identifier: str) -> bool:
        if identifier not in self.loaded_plugins:
            LOGGER.warning(f"Plugin <{identifier}> not loaded.")
            return False

        loaded_rdeps, _ = get_rdeps_plugin(identifier, self.loaded_deps_table)
        await self._batch_unload(loaded_rdeps, False)
        failed_list = await self._batch_load(loaded_rdeps[::-1], self.info_deps_table)
        if failed_list:
            for failed_id in failed_list:
                LOGGER.warning(f"Plugin <{failed_id}> not loaded.")
            LOGGER.error(f"Failed to reload <{identifier}> .")
            return False

        LOGGER.info(f"Successfully reload <{identifier}> .")
        return True

    async def reload_all(self) -> None:
        await self.unload_all()
        await self.load_all()


plugin_manager = PluginManager()


__all__ = [
    "plugin_manager",
]
