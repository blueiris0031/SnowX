from pathlib import Path

from .metadata import metadata_loader
from ..path import dir_plugin_path
from ...types.plugin import (
    Metadata,
    PathInfo,
    Info,
)


def path_info_loader(plugin_path: Path, metadata: Metadata) -> PathInfo:
    return PathInfo(
        plugin_path,
        f"{plugin_path.parent.name}.{plugin_path.name}.{metadata.entry_point}",
    )


def info_loader(path_info: PathInfo, metadata: Metadata) -> Info:
    return Info(path_info, metadata)


def get_plugin_info(plugin_path: Path) -> Info | None:
    available, metadata = metadata_loader(plugin_path)
    if not available:
        return None

    path_info = path_info_loader(plugin_path, metadata)
    return info_loader(path_info, metadata)


def get_all_plugin_info() -> list[Info]:
    return [
        info
        for path in dir_plugin_path()
        if (info := get_plugin_info(path)) is not None
    ]


__all__ = [
    "get_all_plugin_info",
]
