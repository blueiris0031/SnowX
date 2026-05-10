import json
from pathlib import Path
from traceback import format_exc
from typing import Any, Callable

from ..utils.path import get_main_path


class ConfigManager:
    def __init__(self):
        self._config_path = get_main_path().parent / "config.json"
        self._init_fconfig()

    @property
    def config_path(self) -> Path:
        return self._config_path

    def _init_fconfig(self) -> None:
        self._infile_config: dict[str, Any] = {}
        self._correct_config: dict[str, Any] = {}

        try:
            with open(self.config_path, "r") as f:
                raw_config = json.load(f)
            if not isinstance(raw_config, dict):
                return
            self._infile_config.update(raw_config)

        except Exception:
            print(format_exc())

    def get_config(
            self,
            key: str,
            default: Any,
            checker: Callable[..., bool] | None = None,
            *checker_args: Any,
            **checker_kwargs: Any
    ) -> Any:
        if key in self._correct_config:
            return self._correct_config[key]

        result = self._infile_config.get(key, default)
        if (
            not isinstance(result, type(default))
            or (
                checker is not None
                and checker(result, *checker_args, **checker_kwargs)
            )
        ):
            result = default

        self._correct_config[key] = result
        return result

    def rewrite_config(self) -> None:
        try:
            with open(self.config_path, "w", encoding="utf8") as f:
                f.write(json.dumps(self._correct_config, indent=4, ensure_ascii=False))
        except Exception:
            print(format_exc())


config_manager = ConfigManager()


__all__ = [
    "config_manager",
]
