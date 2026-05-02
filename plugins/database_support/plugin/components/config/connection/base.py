from abc import ABC, abstractmethod
from typing import Any, Optional, Type


class BaseConnectionConfigGenerator(ABC):
    _generator_map = {}

    @classmethod
    def get_generator(cls, db_type: str) -> Optional[Type["BaseConnectionConfigGenerator"]]:
        return cls._generator_map.get(db_type, None)

    @classmethod
    def set_generator(cls, db_type: str, generator: Type["BaseConnectionConfigGenerator"]) -> None:
        cls._generator_map.setdefault(db_type, generator)

    @classmethod
    def del_generator(cls, db_type: str) -> Optional[Type["BaseConnectionConfigGenerator"]]:
        cls._generator_map.pop(db_type, None)

    def __init_subclass__(cls, db_type: str | None = None) -> None:
        if db_type is None:
            return

        cls.set_generator(db_type, cls)

    @classmethod
    @abstractmethod
    def get_engine(cls) -> str: ...

    @classmethod
    @abstractmethod
    def get_credentials(cls, **credentials: Any) -> dict[str, Any]: ...


__all__ = [
    "BaseConnectionConfigGenerator",
]
