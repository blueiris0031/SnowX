from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from snowx.api.logger import get_logger


class BaseReader(ABC):
    _type_map = {}
    _logger = get_logger("SnowXConfigReader")

    def __init_subclass__(cls, allow_type: str) -> None:
        if allow_type not in cls._type_map:
            cls._type_map[allow_type] = cls

    @classmethod
    def get_reader(cls, type_: str) -> Optional["BaseReader"]:
        return cls._type_map.get(type_, None)

    def s_read(self, path: Path, **kwargs) -> dict:
        try:
            self._logger.info(f"Trying to read [{path}]...")
            result = self.read(path, **kwargs)
            if not isinstance(result, dict):
                raise TypeError(f'Reading result of the [{path}] is not a dict')

            return result
        except Exception as e:
            self._logger.error(f"Failed to read [{path}], use empty dict.", exc_info=e)
            return {}

    def s_write(self, path: Path, data: dict, **kwargs) -> None:
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
