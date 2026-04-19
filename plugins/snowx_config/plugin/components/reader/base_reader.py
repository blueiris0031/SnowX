from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Type

from snowx.api.logger import get_logger


class BaseReader(ABC):
    _type_map = {}
    _logger = get_logger("SnowXConfigReader")

    def __init_subclass__(cls, allow_type: str, cover: bool = False) -> None:
        cls.register_reader(allow_type, cls, cover)

    @classmethod
    def register_reader(cls, allow_type: str, reader: Type["BaseReader"], cover: bool = False) -> None:
        if allow_type in cls._type_map and not cover:
            return
        cls._type_map[allow_type] = reader

    @classmethod
    def cancel_reader(cls, allow_type: str) -> None:
        cls._type_map.pop(allow_type, None)

    @classmethod
    def get_reader(cls, allow_type: str) -> Optional["BaseReader"]:
        return cls._type_map.get(allow_type, None)

    def safe_read(self, path: Path, **kwargs) -> dict:
        try:
            self._logger.info(f"Trying to read [{path}]...")
            result = self.read(path, **kwargs)
            if not isinstance(result, dict):
                raise TypeError(f'Reading result of the [{path}] is not a dict')

            return result
        except Exception as e:
            self._logger.error(f"Failed to read [{path}], use empty dict.", exc_info=e)
            return {}

    def safe_write(self, path: Path, data: dict, **kwargs) -> None:
        try:
            self._logger.info(f"Trying to write [{path}] ...")
            if not isinstance(data, dict):
                raise TypeError(f'Data to be written to the [{path}] is not a dict')

            self.write(path, data, **kwargs)
        except Exception as e:
            self._logger.error(f"Failed to write [{path}].", exc_info=e)

    @abstractmethod
    def read(self, path: Path, **kwargs) -> dict: ...

    @abstractmethod
    def write(self, path: Path, data: dict, **kwargs) -> None: ...


__all__ = [
    "BaseReader",
]
