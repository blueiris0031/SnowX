from tortoise.exceptions import ConfigurationError

from ...base.config.connection import BaseConnectionConfigGenerator


class SqliteConnectionConfigGenerator(BaseConnectionConfigGenerator, db_type="sqlite"):
    @classmethod
    def get_engine(cls) -> str:
        return "tortoise.backends.sqlite"

    @classmethod
    def get_credentials(cls, **credentials: str) -> dict[str, str]:
        is_memory_db = credentials.get("is_memory_db", False)
        if is_memory_db:
            db_path = ":memory:"
        else:
            db_path = credentials.get("db_path", "")

        if not db_path:
            raise ConfigurationError("Invalid SQLite file path")

        return {"file_path": db_path}


__all__ = [
    "SqliteConnectionConfigGenerator",
]
