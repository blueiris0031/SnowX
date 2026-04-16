from abc import ABC, abstractmethod
from typing import Optional, Type

from pydantic import BaseModel
from snowx.api.logger import get_logger


class BaseConverter(ABC):
    _name_map = {}
    _logger = get_logger("SnowXConfigConverter")

    def __init_subclass__(cls, name: str) -> None:
        if name not in cls._name_map:
            cls._name_map[name] = cls

    @classmethod
    def get_converter(cls, name: str) -> Optional["BaseConverter"]:
        return cls._name_map.get(name, None)

    def s_load(self, n_data: dict, model: Type[BaseModel], **kwargs) -> BaseModel | None:
        try:
            self._logger.info(f"Trying to load data...")
            return self.load(n_data, model, **kwargs)
        except Exception as e:
            self._logger.error(f"Failed to load data.", exc_info=e)
            return None

    def s_dump(self, s_data: BaseModel, **kwargs) -> dict:
        try:
            self._logger.info(f"Trying to dump data...")
            result = self.dump(s_data, **kwargs)
            if not isinstance(result, dict):
                raise TypeError("Dumped data is not a dictionary")

            return result
        except Exception as e:
            self._logger.error(f"Failed to dump data.", exc_info=e)
            return {}

    @abstractmethod
    def load(self, n_data: dict, model: Type[BaseModel], **kwargs) -> BaseModel: ...

    @abstractmethod
    def dump(self, s_data: BaseModel, **kwargs) -> dict: ...


__all__ = [
    "BaseConverter",
]
