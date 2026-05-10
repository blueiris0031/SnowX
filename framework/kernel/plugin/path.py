from pathlib import Path

from ...constants.path import PATH
from ...utils.path import is_valid_name


def dir_plugin_path() -> tuple[Path, ...]:
    if not PATH.PLUGINS.is_dir():
        return ()

    return tuple(path for path in PATH.PLUGINS.iterdir() if path.is_dir() and is_valid_name(path.name))
