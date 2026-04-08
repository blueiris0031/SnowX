from typing import Any, Type
from abc import ABC, abstractmethod
from copy import copy


class BaseConfig(ABC):
    _type_map = {}

    def __init__(self, default: Any):
        self._default = default

    def __init_subclass__(cls, allow_type: Type | None = None):
        if allow_type is None:
            return

        cls._type_map[allow_type] = cls

    @property
    def default(self) -> Any:
        return self._default

    @abstractmethod
    def verify_config(self, config: Any) -> bool: ...

    @abstractmethod
    def get_default_config(self) -> Any: ...


class BaseContainerConfig(BaseConfig):
    @property
    def default(self) -> Any:
        return copy(self._default)


class DictConfig(BaseContainerConfig, allow_type=dict):
    def __init__(self, default: dict[str, Any]):
        super().__init__(default)

    def verify_config(self, config: dict[str, Any]) -> bool:



class RootConfig(DictConfig):

