from dataclasses import dataclass
from pathlib import Path
from typing import Type

import yaml
from snowx.api.logger import get_logger
from snowx.api.path import get_config_path
from snowx.api.plugin import get_id_from_stack
from snowx.utils.path import is_valid_filename


LOGGER = get_logger("SnowXConfigManager")


def _read_yaml(path: "Path") -> dict:
    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data

    except Exception as e:
        LOGGER.error(f"Failed to load yaml <{str(path)}> config", exc_info=e)
        return {}


def _write_yaml(path: "Path", data: dict) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

    except Exception as e:
        LOGGER.error(f"Failed to save yaml <{str(path)}> config", exc_info=e)


VALID_TYPE = (str, int, float, bool, list, dict)
VALID_TYPING = str | int | float | bool | list | dict


@dataclass(frozen=True)
class ConfigMetadata:
    type: Type[VALID_TYPING]
    default: VALID_TYPING


def auto_config(default: VALID_TYPING) -> ConfigMetadata:
    config_type = type(default)
    if config_type not in VALID_TYPE:
        raise TypeError(f"Invalid type: <{config_type}>")

    return ConfigMetadata(config_type, default)


@dataclass(frozen=False)
class ConfigItem:
    metadata: ConfigMetadata
    value: VALID_TYPING


class ConfigContainer:
    def __init__(self, path: Path, **metadata: ConfigMetadata) -> None:
        self.path = path
        self.metadata = metadata

        self.config: dict[str, "ConfigItem"] = {}
        self._load()

    def _load(self):
        raw_config = _read_yaml(self.path)

        write_back = False
        for key, value in self.metadata.items():
            if key in raw_config and isinstance(raw_config[key], value.type):
                continue

            write_back = True
            raw_config[key] = value.default

        useless_list = []
        for key in raw_config.keys():
            if key in self.metadata:
                continue

            write_back = True
            useless_list.append(key)

        for key in useless_list:
            del raw_config[key]

        for key, value in raw_config.items():
            self.config[key] = ConfigItem(self.metadata[key], value)

        if write_back:
            self._write()

    def _write(self) -> None:
        raw_config = {key: item.value for key, item in self.config.items()}
        _write_yaml(self.path, raw_config)

    def get(self, key: str) -> VALID_TYPING:
        if key not in self.config:
            raise KeyError(f"Invalid key: <{key}>")

        return self.config[key].value

    def set(self, key: str, value: VALID_TYPING) -> None:
        if key not in self.config:
            raise KeyError(f"Invalid key: <{key}>")

        current_item = self.config[key]
        if not isinstance(value, current_item.metadata.type):
            raise TypeError(f"Invalid value: <{value}>")

        current_item.value = value
        self._write()


def get_config(name: str | None = None, **metadata: ConfigMetadata) -> ConfigContainer:
    name = get_id_from_stack(name, level=2)
    return ConfigContainer(get_config_path(f"{name}.yml"), **metadata)


__all__ = [
    "auto_config",
    "get_config",
]
