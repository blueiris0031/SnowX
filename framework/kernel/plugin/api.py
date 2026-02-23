from inspect import stack

from .manager import plugin_manager
from ...types.plugin import Info, Item


def refresh_infos() -> None:
    plugin_manager.update_plugin_infos()


async def load_plugin(identifier: str) -> bool:
    return await plugin_manager.load_single(identifier)


async def unload_plugin(identifier: str, force: bool = False) -> None:
    await plugin_manager.unload_single(identifier, force)


async def reload_plugin(identifier: str) -> bool:
    return await plugin_manager.reload_single(identifier)


async def reload_all() -> None:
    await plugin_manager.reload_all()


def get_info(identifier: str) -> Info | None:
    if identifier in plugin_manager.loaded_plugins:
        return plugin_manager.loaded_plugins[identifier].info

    return plugin_manager.plugin_infos.get(identifier, None)


def get_item(identifier: str) -> Item | None:
    return plugin_manager.loaded_plugins.get(identifier, None)


def get_loaded_plugins() -> tuple[str]:
    return tuple(plugin_manager.loaded_plugins.keys())


def get_unloaded_plugins() -> tuple[str]:
    loaded = plugin_manager.loaded_plugins
    return tuple(
        key
        for key in plugin_manager.plugin_infos.keys()
        if key not in loaded
    )


def get_id_from_stack(identifier: str | None = None, level: int = 1) -> str:
    if isinstance(identifier, str) and identifier:
        return identifier

    try:
        frame = stack(0)[level].frame
    except IndexError:
        return ""

    metadata = frame.f_globals.get("__plugin_metadata__", None)
    return getattr(metadata, "id", "")


def get_plugin_id() -> str:
    return get_id_from_stack(level=2)


__all__ = [
    "refresh_infos",
    "load_plugin",
    "unload_plugin",
    "reload_plugin",
    "reload_all",
    "get_info",
    "get_item",
    "get_loaded_plugins",
    "get_unloaded_plugins",
    "get_id_from_stack",
    "get_plugin_id",
]
