import json
import re
from pathlib import Path
from typing import Any, Callable

from ..logger import get_logger
from ...error.version import InvalidVersionValueError
from ...types.plugin import (
    Metadata,
    DependentPlugin,
)
from ...utils.version import Version


METADATA_FILENAME = "metadata.json"

LOGGER = get_logger("MetadataLoader")


def _generic_err_logger(plugin_path: Path, message: str, exc_info: Exception | None = None) -> None:
    LOGGER.error(f"Failed to load <{METADATA_FILENAME}> from <{plugin_path}>: {message}", exc_info=exc_info)


def _get_raw_metadata(plugin_path: Path) -> tuple[bool, dict | None]:
    metadata_path = plugin_path / METADATA_FILENAME

    if not metadata_path.is_file():
        _generic_err_logger(plugin_path, "Not a file or does not exist.")
        return False, None

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            raw_metadata = json.load(f)

    except Exception as exc:
        _generic_err_logger(plugin_path, "Loading abnormality.", exc_info=exc)
        return False, None

    if not isinstance(raw_metadata, dict):
        _generic_err_logger(plugin_path, "Unsupported format.")
        return False, None

    return True, raw_metadata


def _generic_string_checker(key: str, plugin_path: Path, raw_metadata: dict[str, Any], pattern: re.Pattern | None = None) -> tuple[bool, str | None]:
    if key not in raw_metadata:
        _generic_err_logger(plugin_path, f"<{key}> not present in metadata.")
        return False, None

    raw_data = raw_metadata[key]
    if not isinstance(raw_data, str):
        _generic_err_logger(plugin_path, f"Unsupported <{key}> type.")
        return False, None

    if pattern is not None and re.fullmatch(pattern, raw_data) is None:
        _generic_err_logger(plugin_path, f"Unsupported <{key}> format.")
        return False, None

    return True, raw_data

PLUGIN_ID_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]$')

def _plugin_id_loader(plugin_path: Path, raw_metadata: dict[str, Any]) -> tuple[bool, str | None]:
    general_check, raw_plugin_id = _generic_string_checker("PluginID", plugin_path, raw_metadata, PLUGIN_ID_PATTERN)
    if not general_check:
        return False, None

    return True, raw_plugin_id

def _plugin_name_loader(plugin_path: Path, raw_metadata: dict[str, Any]) -> tuple[bool, str | None]:
    return _generic_string_checker("PluginName", plugin_path, raw_metadata)

def _plugin_version_loader(plugin_path: Path, raw_metadata: dict[str, Any]) -> tuple[bool, Version | None]:
    general_check, raw_plugin_version = _generic_string_checker("PluginVersion", plugin_path, raw_metadata)
    if not general_check:
        return False, None

    try:
        plugin_version = Version(raw_plugin_version)

    except InvalidVersionValueError:
        _generic_err_logger(plugin_path, "Unsupported <PluginVersion> format.")
        return False, None

    if plugin_version.has_wildcard:
        _generic_err_logger(plugin_path, "Wildcards are not allowed in the version.")
        return False, None

    return True, plugin_version

ENTRY_POINT_PATTERN = PLUGIN_ID_PATTERN

def _entry_point_loader(plugin_path: Path, raw_metadata: dict[str, Any]) -> tuple[bool, str | None]:
    general_check, raw_entry_point = _generic_string_checker("EntryPoint", plugin_path, raw_metadata, ENTRY_POINT_PATTERN)
    if not general_check:
        return False, None

    return True, raw_entry_point

REQUIRED_KEYS: dict[str, Callable[[Path, dict[str, Any]], tuple[bool, Any | None]]] = {
    "id": _plugin_id_loader,
    "name": _plugin_name_loader,
    "version": _plugin_version_loader,
    "entry_point": _entry_point_loader,
}

def _description_loader(_, raw_metadata: dict[str, Any]) -> tuple[bool, str | None]:
    description = raw_metadata.get("Description", "")
    if not isinstance(description, str):
        return True, ""
    return True, description

def _conv_version(raw_version: list[str | None]) -> tuple[()] | tuple[Version | None] | tuple[Version | None, Version | None]:
    result: list[Version | None] = []
    if not 1 <= len(raw_version) <= 2:
        return ()

    for version in raw_version:
        if version is None:
            result.append(None)
        else:
            result.append(Version(version))

    return tuple[Version | None](result)

def _dependent_framework_version_loader(plugin_path: Path, raw_metadata: dict[str, Any]) -> tuple[bool, tuple[Version | None, ...] | None]:
    dependent_snowx_versions = raw_metadata.get("DependentSnowxVersion", [])
    if not isinstance(dependent_snowx_versions, list):
        _generic_err_logger(plugin_path, "The format of dependent <SnowX> version is incorrect.")
        return False, None
    if not (0 <= len(dependent_snowx_versions) <= 2):
        _generic_err_logger(plugin_path, "The format of dependent <SnowX> version is incorrect.")
        return False, None
    try:
        loaded_versions = _conv_version(dependent_snowx_versions)
        return True, tuple(loaded_versions)
    except InvalidVersionValueError:
        _generic_err_logger(plugin_path, "Unsupported <SnowX> version.")
        return False, None

def _dependent_plugins_loader(plugin_path: Path, raw_metadata: dict[str, Any]) -> tuple[bool, tuple[DependentPlugin, ...] | None]:
    dependent_plugins_data = raw_metadata.get("DependentPlugins", {})
    if not isinstance(dependent_plugins_data, dict):
        _generic_err_logger(plugin_path, "The format of plugin dependent information is incorrect.")
        return False, None

    dependent_plugins = []
    for dependent_plugin_id, dependent_version in dependent_plugins_data.items():
        try:
            dependent_plugins.append(
                DependentPlugin(
                    dependent_plugin_id,
                    tuple(_conv_version(dependent_version)),
                )
            )
            continue
        except InvalidVersionValueError as e:
            _generic_err_logger(plugin_path, str(e))
            return False, None

    return True, tuple(dependent_plugins)

def _dependent_modules_loader(plugin_path: Path, raw_metadata: dict[str, Any]) -> tuple[bool, tuple[str, ...] | None]:
    dependent_modules = raw_metadata.get("DependentModules", [])
    if not isinstance(dependent_modules, list):
        _generic_err_logger(plugin_path, "The format of module dependent information is incorrect.")
        return False, None

    if any(not isinstance(module_name, str) for module_name in dependent_modules):
        _generic_err_logger(plugin_path, "Unsupported <ModuleName> types.")
        return False, None

    return True, tuple(dependent_modules)

OPTIONAL_KEYS: dict[str, Callable[[Path, dict[str, Any]], tuple[bool, Any | None]]] = {
    "description": _description_loader,
    "dependent_framework_version": _dependent_framework_version_loader,
    "dependent_plugins": _dependent_plugins_loader,
    "dependent_modules": _dependent_modules_loader,
}


def _generic_metadata_loader(
        keys: dict[str, Callable[[Path, dict[str, Any]], tuple[bool, Any | None]]],
        plugin_path: Path,
        raw_metadata: dict[str, Any],
) -> tuple[bool, dict[str, Any] | None]:
    metadata: dict[str, Any] = {}
    for key, loader in keys.items():
        is_success, data = loader(plugin_path, raw_metadata)
        if not is_success:
            return False, None

        metadata[key] = data

    return True, metadata

def _required_metadata_loader(plugin_path: Path, raw_metadata: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
    return _generic_metadata_loader(REQUIRED_KEYS, plugin_path, raw_metadata)

def _optional_metadata_loader(plugin_path: Path, raw_metadata: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
    return _generic_metadata_loader(OPTIONAL_KEYS, plugin_path, raw_metadata)


def metadata_loader(plugin_path: Path) -> tuple[bool, Metadata | None]:
    load_raw_data_success, raw_metadata = _get_raw_metadata(plugin_path)
    if not load_raw_data_success:
        return False, None

    load_required_success, required_metadata = _required_metadata_loader(plugin_path, raw_metadata)
    if not load_required_success:
        return False, None

    load_optional_success, optional_metadata = _optional_metadata_loader(plugin_path, raw_metadata)
    if not load_optional_success:
        return False, None

    return True, Metadata(**required_metadata, **optional_metadata)


__all__ = [
    "metadata_loader",
]
