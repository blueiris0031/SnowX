from pathlib import Path
from typing import Callable

from ..constants.path import PATH
from ..utils.path import is_valid_name


def _get_file_path(parent: Path, file_name: str) -> Path:
    if not is_valid_name(file_name.replace(".", "")):
        raise ValueError(file_name)
    if not (fpath := parent / file_name).is_file():
        fpath.touch(0o666)
    return fpath


def _get_folder_path(parent: Path, folder_name: str) -> Path:
    if not is_valid_name(folder_name):
        raise ValueError(folder_name)
    if not (fpath := parent / folder_name).is_dir():
        fpath.mkdir(parents=True)
    return fpath


def _new_getter(base_getter: Callable[[Path, str], Path], parent: Path) -> Callable[[str], Path]:
    return lambda name: base_getter(parent, name)


get_config_path = _new_getter(_get_file_path, PATH.CONFIG)
get_data_path = _new_getter(_get_folder_path, PATH.DATA)
get_log_path = _new_getter(_get_folder_path, PATH.LOGS)
get_temp_path = _new_getter(_get_folder_path, PATH.TEMP)


__all__ = [
    "get_config_path",
    "get_data_path",
    "get_log_path",
    "get_temp_path",
]
