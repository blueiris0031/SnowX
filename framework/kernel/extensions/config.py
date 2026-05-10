import json
from traceback import print_exc
from typing import Any, Callable, TypeVar

from ...base.kernel import AbstractKernelExtension
from ...base.lifecycle import BaseLifeCycle
from ...constants.logger import ROOT_NAME
from ...mixins.loggable import LoggableMixin
from ...utils.pathtools import get_root_path


_C = TypeVar("_C", bound=object)


class ConfigExtension(BaseLifeCycle, AbstractKernelExtension, LoggableMixin):
    @property
    def identifier(self) -> str:
        return "config"

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ()

    def __init__(self) -> None:
        super().__init__()

        self._config_path = get_root_path() / "config.json"
        self._infile_config: dict[str, Any] = {}
        self._correct_config: dict[str, Any] = {}

        self.set_logger(f"{ROOT_NAME}.{self.identifier}")

    def _load_infile_config(self) -> None:
        if not self._config_path.is_file():
            self._config_path.touch()
            self.logger.info(f"Creating new config file at '{self._config_path}'")
        try:
            with open(self._config_path, "r") as f:
                raw_config = json.load(f)
            if not isinstance(raw_config, dict):
                self.logger.error(f"Incorrect configuration file data.")
                return
            self._infile_config.update(raw_config)
        except Exception as e:
            self.logger.error(f"Unsupported config file at '{self._config_path}'", exc_info=e)

    def _rewrite_config(self) -> None:
        try:
            with open(self._config_path, "w", encoding="utf8") as f:
                f.write(json.dumps({**self._infile_config, **self._correct_config}, indent=4, ensure_ascii=False))
        except Exception:
            print_exc()

    def get_config(self, key: str, default: Any, checker: Callable[[object], bool] | None = None) -> Any:
        if key in self._correct_config:
            return self._correct_config[key]
        if key not in self._infile_config:
            return self._correct_config.setdefault(key, default)
        f_config = self._infile_config.get(key, default)
        if checker is None:
            return self._correct_config.setdefault(key, f_config if isinstance(f_config, type(default)) else default)
        return self._correct_config.setdefault(key, f_config if checker(f_config) else default)

    def real_start(self) -> None:
        self._load_infile_config()

    def real_stop(self, force: bool = False) -> None:
        self._rewrite_config()


__all__ = [
    "ConfigExtension",
]
