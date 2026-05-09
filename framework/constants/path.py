from dataclasses import dataclass
from pathlib import Path

from ..kernel.config import config_manager
from ..utils.path import is_valid_filename, get_main_path


@dataclass(frozen=True)
class ConstantPath:
    BASE: Path = get_main_path().parent
    MAIN: Path = BASE / "framework"
    CONFIG: Path = BASE / config_manager.get_config("CONFIG_DIR_NAME", "config", is_valid_filename)
    DATA: Path = BASE / config_manager.get_config("DATA_DIR_NAME", "data", is_valid_filename)
    LOGS: Path = BASE / config_manager.get_config("LOGS_DIR_NAME", "logs", is_valid_filename)
    PLUGINS: Path = BASE / config_manager.get_config("PLUGINS_DIR_NAME", "plugins", is_valid_filename)
    TEMP: Path = BASE / config_manager.get_config("TEMP_DIR_NAME", "temp", is_valid_filename)
    TOOLS: Path = BASE / config_manager.get_config("TOOLS_DIR_NAME", "tools", is_valid_filename)


PATH = ConstantPath()


__all__ = [
    "PATH",
]
