from pathlib import Path
from typing import Callable

from ..constants.path import PATH
from ..utils.path import is_valid_filename


def _get_file_path(file_name: str, parent: Path) -> Path:
    if not is_valid_filename(file_name.replace(".", "")):
        raise ValueError(file_name)

    fpath = parent / file_name
    if not fpath.is_file():
        fpath.touch(0o666)

    return fpath


def _get_folder_path(folder_name: str, parent: Path) -> Path:
    if not is_valid_filename(folder_name):
        raise ValueError(folder_name)

    fpath = parent / folder_name
    if not fpath.is_dir():
        fpath.mkdir(parents=True)

    return fpath


def _new_getter(base_getter: Callable[[str, Path], Path], parent: Path) -> Callable[[str], Path]:
    def getter(name: str) -> Path:
        return base_getter(
            name,
            parent,
        )

    return getter


get_config_path = _new_getter(_get_file_path, PATH.CONFIG)
get_data_path = _new_getter(_get_folder_path, PATH.DATA)
get_log_path = _new_getter(_get_folder_path, PATH.LOGS)
get_temp_path = _new_getter(_get_folder_path, PATH.TEMP)


def dir_plugin_path() -> tuple[Path, ...]:
    if not PATH.PLUGINS.is_dir():
        return ()

    return tuple(
        path
        for path in PATH.PLUGINS.iterdir()
        if path.is_dir() and
        is_valid_filename(path.name)
    )


__all__ = [
    "get_config_path",
    "get_data_path",
    "get_log_path",
    "get_temp_path",
    "dir_plugin_path",
]
