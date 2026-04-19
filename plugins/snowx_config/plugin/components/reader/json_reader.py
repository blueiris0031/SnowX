import json
from pathlib import Path
from typing import Any

from .base_reader import BaseReader


class JsonReader(BaseReader, allow_type="json"):
    _file_suffix = "json"

    _r_default_read_kwargs = {}
    _r_default_write_kwargs = {
        "ensure_ascii": False,
        "indent": 4,
    }

    def __init__(
            self,
            encoding: str = 'utf-8',
            read_kwargs: dict[str, Any] | None = None,
            write_kwargs: dict[str, Any] | None = None,
    ):
        self._encoding = encoding
        if isinstance(read_kwargs, dict):
            self._default_read_kwargs = {**self._r_default_read_kwargs, **read_kwargs}
        if isinstance(write_kwargs, dict):
            self._default_write_kwargs = {**self._r_default_write_kwargs, **write_kwargs}

    def read(self, path: Path, **kwargs: Any) -> dict:
        with open(path, "r", encoding=self._encoding) as f:
            return json.load(f, **{**self._default_read_kwargs, **kwargs})

    def write(self, path: Path, data: Any, **kwargs: Any) -> None:
        with open(path, "w", encoding=self._encoding) as f:
            json.dump(data, f, **{**self._default_write_kwargs, **kwargs})


__all__ = [
    "JsonReader",
]
