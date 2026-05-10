from abc import ABC, abstractmethod
from typing import Optional, Type, Callable

from pydantic import BaseModel
from snowx.api.logger import LoggerManager


class BaseConverter(ABC):
    _name_map: dict[str, Type["BaseConverter"]] = {}
    _logger = LoggerManager().get_logger("SnowXConfigConverter")

    def __init_subclass__(cls, name: str, cover: bool = False) -> None:
        cls.register_converter(name, cls, cover)

    @classmethod
    def register_converter(cls, name: str, converter: Type["BaseConverter"], cover: bool) -> None:
        if name in cls._name_map and not cover:
            return
        cls._name_map[name] = converter

    @classmethod
    def cancel_converter(cls, name: str) -> None:
        cls._name_map.pop(name, None)

    @classmethod
    def get_converter(cls, name: str) -> Optional[Type["BaseConverter"]]:
        return cls._name_map.get(name, None)

    @abstractmethod
    def load(self, n_data: dict, call: Callable[..., BaseModel], **kwargs) -> BaseModel: ...

    @abstractmethod
    def dump(self, s_data: BaseModel, **kwargs) -> dict: ...

    def safe_load(self, n_data: dict, call: Callable[..., BaseModel], **kwargs) -> BaseModel | None:
        try:
            self._logger.info(f"Trying to load data...")
            return self.load(n_data, call, **kwargs)
        except Exception as e:
            self._logger.error(f"Failed to load data.", exc_info=e)
            return None

    def safe_dump(self, s_data: BaseModel, **kwargs) -> dict:
        try:
            self._logger.info(f"Trying to dump data...")
            result = self.dump(s_data, **kwargs)
            if not isinstance(result, dict):
                raise TypeError("Dumped data is not a dict")

            return result
        except Exception as e:
            self._logger.error(f"Failed to dump data.", exc_info=e)
            return {}


__all__ = [
    "BaseConverter",
]
