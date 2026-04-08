from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from tortoise import TortoiseConfig
from tortoise.config import ConnectionConfig


class BaseConnectionsConfigGenerator(ABC):
    _engine_map = {}

    @classmethod
    def get_generator(cls, db_type: str) -> Optional[Type["BaseConnectionsConfigGenerator"]]:
        return cls._engine_map.get(db_type, None)

    @classmethod
    def set_generator(cls, db_type: str, generator: Type["BaseConnectionsConfigGenerator"]) -> None:
        cls._engine_map.setdefault(db_type, generator)

    @classmethod
    def del_generator(cls, db_type: str) -> Optional[Type["BaseConnectionsConfigGenerator"]]:
        cls._engine_map.pop(db_type, None)

    def __init_subclass__(cls, db_type: str) -> None:
        cls.set_generator(db_type, cls)

    @classmethod
    @abstractmethod
    def get_engine(cls) -> str: ...

    @classmethod
    @abstractmethod
    def get_credentials(cls, **kwargs: Any) -> dict[str, Any]: ...


def get_connections_config(db_type: str, **db_config) -> ConnectionConfig:
    generator = BaseConnectionsConfigGenerator.get_generator(db_type)
    if generator is None:
        raise ValueError(f"Unknown database type: {db_type}")

    return ConnectionConfig(
        engine=generator.get_engine(),
        credentials=generator.get_credentials(**db_config)
    )


def get_config() -> TortoiseConfig:
    return TortoiseConfig()
