from dataclasses import dataclass
from pathlib import Path

from ..kernel.config import get_config
from ..utils.path import is_valid_filename


@dataclass(frozen=True)
class ConstantPath:
    BASE: Path = Path.cwd()
    MAIN: Path = BASE / "framework"
    CONFIG: Path = BASE / get_config("CONFIG_DIR_NAME", "config", is_valid_filename)
    DATA: Path = BASE / get_config("DATA_DIR_NAME", "data", is_valid_filename)
    LOGS: Path = BASE / get_config("LOGS_DIR_NAME", "logs", is_valid_filename)
    PLUGINS: Path = BASE / get_config("PLUGINS_DIR_NAME", "plugins", is_valid_filename)
    TEMP: Path = BASE / get_config("TEMP_DIR_NAME", "temp", is_valid_filename)


PATH = ConstantPath()


__all__ = [
    "PATH",
]
