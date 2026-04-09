from typing import Any

from tortoise.config import ConnectionConfig
from tortoise.exceptions import ConfigurationError

from ...base.config.connection import BaseConnectionConfigGenerator


def get_connection_config(db_type: str, **credentials: Any) -> ConnectionConfig:
    generator = BaseConnectionConfigGenerator.get_generator(db_type)
    if generator is None:
        raise ConfigurationError(f"Unknown database type: {db_type}")

    return ConnectionConfig(
        engine=generator.get_engine(),
        credentials=generator.get_credentials(**credentials)
    )


__all__ = [
    "get_connection_config",
]
