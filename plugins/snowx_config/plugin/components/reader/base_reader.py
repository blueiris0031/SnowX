from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Type

from snowx.api.logger import get_logger

from ..clock import clock_worker


class BaseReader(ABC):
    _type_map: dict[str, Type["BaseReader"]] = {}
    _logger = get_logger("SnowXConfigReader")

    def __init_subclass__(cls, file_type: str, cover: bool = False) -> None:
        cls.register_reader(file_type, cls, cover)

    @classmethod
    def register_reader(cls, file_type: str, reader: Type["BaseReader"], cover: bool = False) -> None:
        if file_type in cls._type_map and not cover:
            return
        cls._type_map[file_type] = reader

    @classmethod
    def cancel_reader(cls, file_type: str) -> None:
        cls._type_map.pop(file_type, None)

    @classmethod
    def get_reader(cls, file_type: str) -> Optional[Type["BaseReader"]]:
        return cls._type_map.get(file_type, None)

    @property
    @abstractmethod
    def _file_suffix(self) -> str: ...

    @abstractmethod
    def read(self, path: Path, **kwargs) -> dict: ...

    @abstractmethod
    def write(self, path: Path, data: dict, **kwargs) -> None: ...

    @property
    def file_suffix(self) -> str:
        return self._file_suffix

    def safe_read(self, path: Path, **kwargs) -> dict:
        try:
            self._logger.info(f"Trying to read [{path}]...")
            result = self.read(path, **kwargs)
            if not isinstance(result, dict):
                raise TypeError(f"Reading result of the [{path}] is not a dict")

            return result
        except Exception as e:
            self._logger.error(f"Failed to read [{path}], use empty dict.", exc_info=e)
            return {}

    def _real_write(self, path: Path, data: dict, **kwargs) -> None:
        try:
            self._logger.info(f"Trying to write [{path}] ...")
            self.write(path, data, **kwargs)
        except Exception as e:
            self._logger.error(f"Failed to write [{path}].", exc_info=e)

    def safe_write(self, path: Path, data: dict, **kwargs) -> None:
        try:
            if not isinstance(data, dict):
                raise TypeError(f'Data to be written to the [{path}] is not a dict')

            clock_worker.submit_task(path, self._real_write, (path, data), kwargs)
        except Exception as e:
            self._logger.error(f"Failed to write [{path}].", exc_info=e)

    
__all__ = [
    "BaseReader",
]
