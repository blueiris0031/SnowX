from typing import Callable


class URLGeneratorManager:
    def __init__(self):
        self._url_generators: dict[str, Callable[..., str]] = {}

    def add_type(self, db_type: str, generator: Callable[..., str]) -> None:
        if db_type in self._url_generators:
            raise Exception(f"DB type {db_type} already exists")

        self._url_generators[db_type] = generator


