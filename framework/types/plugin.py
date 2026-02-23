from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from ..utils.version import Version


@dataclass(frozen=True)
class DependentPlugin:
    id: str
    required_version: tuple[()] | tuple[Version | None] | tuple[Version | None, Version | None]


@dataclass(frozen=True)
class Metadata:
    id: str
    name: str
    version: Version
    entry_point: str

    description: str
    dependent_framework_version: tuple[()] | tuple[Version | None] | tuple[Version | None, Version | None]
    dependent_plugins: tuple[DependentPlugin, ...]
    dependent_modules: tuple[str, ...]


@dataclass(frozen=True)
class PathInfo:
    file_path: Path
    import_path: str


@dataclass(frozen=True)
class Info:
    path_info: PathInfo
    metadata: Metadata


@dataclass(frozen=True)
class Item:
    info: Info
    module: ModuleType


__all__ = [
    "DependentPlugin",
    "Metadata",
    "PathInfo",
    "Info",
    "Item",
]
