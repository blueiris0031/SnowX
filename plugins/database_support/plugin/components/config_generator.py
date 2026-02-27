from typing import Callable


class ConfigGenerator:
    def __init__(self):
        self._url_generators: dict[str, Callable[..., str]] = {}

    def add_generator(self, db_type: str, generator: Callable[..., str]) -> None:
        if db_type in self._url_generators:
            raise KeyError(f"DB type {db_type} already exists")

        self._url_generators[db_type] = generator

    def get_generator(self, db_type: str) -> Callable[..., str]:
        if db_type not in self._url_generators:
            raise KeyError(f"DB type {db_type} does not exist")

        return self._url_generators[db_type]
