from .manager import PluginManager, plugin_manager
from ...constants.framework import FRAMEWORK_METADATA
from ...constants.callback import CALLBACK_TYPE


def load_check_sx_version(manager: PluginManager, identifier: str) -> bool:
    if identifier not in manager.plugin_infos:
        return False

    dep_version = manager.plugin_infos[identifier].metadata.dependent_framework_version
    return FRAMEWORK_METADATA.VERSION.auto_check(dep_version)

def unload_check_sx_version(*_) -> None:
    return None

plugin_manager.inject_load_func(load_check_sx_version, unload_check_sx_version)


def load_check_dep_plugin(manager: PluginManager, identifier: str) -> bool:
    metadata = manager.plugin_infos[identifier].metadata
    deps_plugin = metadata.dependent_plugins
    for dep_plugin in deps_plugin:
        if dep_plugin.id not in manager.loaded_plugins:
            return False

        loaded_version = manager.loaded_plugins[dep_plugin.id].info.metadata.version
        required_ver = dep_plugin.required_version
        if loaded_version.auto_check(required_ver):
            continue
        return False
    return True

def unload_check_dep_plugin(*_) -> None:
    return None

plugin_manager.inject_load_func(load_check_dep_plugin, unload_check_dep_plugin)


from ...components.module_installer import check_module

async def load_check_module(manager: PluginManager, identifier: str) -> bool:
    metadata = manager.plugin_infos[identifier].metadata
    deps_module = metadata.dependent_modules
    for dep_module in deps_module:
        if not await check_module(dep_module, auto_install=True):
            return False

    return True

def unload_check_module(*_) -> None:
    return None

plugin_manager.inject_load_func(load_check_module, unload_check_module)


from .importer import import_plugin, remove_plugin
from ...types.plugin import Item

def load_import_plugin(manager: PluginManager, identifier: str) -> bool | Item:
    item = import_plugin(manager.plugin_infos[identifier])
    if item is None:
        return False
    return item

def unload_import_plugin(manager: PluginManager, identifier: str, _) -> None:
    if identifier not in manager.loaded_plugins:
        return
    info = manager.loaded_plugins[identifier].info
    remove_plugin(info)

plugin_manager.inject_load_func(load_import_plugin, unload_import_plugin)


from ..callback.container import GlobalCallbackContainer
from ..callback.scheduler import GlobalSchedulerManager
from ...types.callback import CallbackResultItem

global_callback_container = GlobalCallbackContainer()
global_scheduler_manager = GlobalSchedulerManager()

async def load_callback_run(_, identifier: str) -> bool:
    await global_scheduler_manager.start(CALLBACK_TYPE.INIT, identifier)
    init_result: tuple[CallbackResultItem] = await global_scheduler_manager.get_running_item(CALLBACK_TYPE.INIT, identifier).get_result()
    return all(result.is_success for result in init_result)

async def unload_callback_run(_, identifier: str, force: bool) -> None:
    if not force:
        await global_scheduler_manager.start(CALLBACK_TYPE.EXIT, identifier)
        await global_scheduler_manager.get_running_item(CALLBACK_TYPE.EXIT, identifier).get_result()

    global_callback_container.auto_remove(identifier)

plugin_manager.inject_load_func(load_callback_run, unload_callback_run)


async def load_start_cb_scheduler(_, identifier: str) -> bool:
    await global_scheduler_manager.start(CALLBACK_TYPE.PROCESS, identifier)
    await global_scheduler_manager.start(CALLBACK_TYPE.AUTORUN, identifier)
    return True

async def unload_start_cb_scheduler(_, plugin_id: str, force: bool) -> None:
    await global_scheduler_manager.stop(CALLBACK_TYPE.PROCESS, plugin_id, force)
    await global_scheduler_manager.stop(CALLBACK_TYPE.AUTORUN, plugin_id, force)

plugin_manager.inject_load_func(load_start_cb_scheduler, unload_start_cb_scheduler)


__all__ = []
