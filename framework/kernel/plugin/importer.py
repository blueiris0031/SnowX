import importlib.util as imp_util
from sys import modules as sys_modules

from ..logger import get_logger
from ..vmodule.expand import add_plugin, del_plugin
from ...types.plugin import Info as PluginInfo, Item as PluginItem


LOGGER = get_logger("Importer")


_imported: set[str] = set()

def import_plugin(plugin_info: PluginInfo) -> PluginItem | None:
    import_path = plugin_info.path_info.import_path
    metadata = plugin_info.metadata
    plugin_id = metadata.id

    if plugin_id in _imported:
        LOGGER.info(f"<{plugin_id}> is already imported.>")
        return None

    LOGGER.info(f"Try to import <{import_path}>...")
    try:
        spec = imp_util.find_spec(import_path)
    except Exception as e:
        LOGGER.error(f"Failed to find spec from <{import_path}>.", exc_info=e)
        return None

    if spec is None:
        LOGGER.error(f"Failed to find spec from <{import_path}>.")
        return None

    module = imp_util.module_from_spec(spec)

    setattr(module, "__plugin_metadata__", metadata)
    LOGGER.info(f"Injected <__plugin_metadata__> into entry point <{import_path}>.")
    sys_modules[import_path] = module
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        LOGGER.error(f"Failed to import <{import_path}>.", exc_info=e)
        sys_modules.pop(import_path, None)
        return None

    add_plugin(metadata.id, module)
    LOGGER.info(f"Mounted <{import_path}> into <VMODULE>.")
    _imported.add(plugin_id)
    return PluginItem(plugin_info, module)


def remove_plugin(plugin_info: PluginInfo) -> None:
    plugin_id = plugin_info.metadata.id
    if plugin_id not in _imported:
        LOGGER.info(f"<{plugin_id}> not imported.")
        return

    del_plugin(plugin_id)
    LOGGER.info(f"Unmounted <{plugin_info.path_info.import_path}> from <VMODULE>.")
    prefix = plugin_info.path_info.import_path.rsplit(".", maxsplit=1)[0]

    remove_list: list[str] = [name for name in sys_modules.keys() if name.startswith(f"{prefix}.") or name == prefix]
    for remove_name in remove_list:
        LOGGER.info(f"Remove <{remove_name}>...")
        sys_modules.pop(remove_name, None)

    _imported.remove(plugin_id)
    LOGGER.info(f"Removed <{prefix}> successfully.")


__all__ = [
    "import_plugin",
    "remove_plugin",
]
