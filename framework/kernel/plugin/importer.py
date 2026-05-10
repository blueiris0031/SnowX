from sys import modules as sys_modules

from ..logger import LoggerManager
from ..virtual_module import get_virtual_module
from ...constants.logger import LOGGER_NAME
from ...constants.virtual_module import ModulePath
from ...types.plugin import Info, Item
from ...utils.module import pre_injection_import
from ...utils.singleton import configured_singleton


@configured_singleton
class Importer:
    def __init__(self) -> None:
        self._imported_map: dict[str, Item] = {}
        self._virtual_module = get_virtual_module(ModulePath.Plugins)
        self._logger = LoggerManager().get_logger(f"{LOGGER_NAME.PLUGIN}.importer")

    def _register_in_virtual_module(self, identifier: str) -> None:
        identifier, module = (item := self._imported_map[identifier]).info.metadata.id, item.module
        self._virtual_module.register_module(identifier, module, recursive=True)

    def import_plugin(self, info: Info) -> Item | None:
        metadata = info.metadata
        identifier = metadata.id
        if identifier in self._imported_map:
            self._logger.info(f"'{identifier}' already imported.")
            return None

        import_path = info.path_info.import_path
        self._logger.info(f"Try to import <'{identifier}'{import_path}>...")
        try:
            plugin_module = pre_injection_import(import_path, __plugin_metadata__=metadata)
        except Exception as e:
            self._logger.error(f"Failed to import <'{identifier}'{import_path}>.", exc_info=e)
            return None

        self._logger.info(f"Try to register <'{identifier}'{import_path}> in 'VirtualModule'...")
        self._imported_map[identifier] = (item := Item(info, plugin_module))
        try:
            self._register_in_virtual_module(identifier)
        except Exception as e:
            self._logger.error(f"Failed to register <'{identifier}'{import_path}>.", exc_info=e)
            self.cancel_import(info)
            return None
        return item

    def _unregister_in_virtual_module(self, identifier: str) -> None:
        self._virtual_module.get_sub_virtual_module(identifier).cancel_virtual_module()

    def cancel_import(self, info: Info) -> None:
        identifier, import_path = info.metadata.id, info.path_info.import_path
        if identifier not in self._imported_map:
            self._logger.info(f"'{identifier}' is not imported.")
            return

        self._logger.info(f"Try to unregister <'{identifier}'{import_path}>...")
        try:
            self._unregister_in_virtual_module(identifier)
        except Exception as e:
            self._logger.error(f"Failed to unregister <'{identifier}'{import_path}>.", exc_info=e)

        self._logger.info(f"Try to cancel import <'{identifier}'{import_path}>...")
        f_import_path = info.path_info.import_path.rsplit(".", 1)[0]
        for remove_name in [f_import_path, *(name for name in sys_modules.keys() if name.startswith(f"{f_import_path}."))]:
            sys_modules.pop(remove_name, None)
        self._logger.info(f"Cancelled import <'{identifier}'{import_path}> successfully.")


__all__ = [
    "Importer",
]
