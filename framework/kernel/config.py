import json
from pathlib import Path
from traceback import format_exc
from typing import Any, Callable


CONFIG_PATH = Path.cwd() / "config.json"

_infile_config: dict[str, Any] = {}
_effective_config = {}


def _init() -> None:
    if not CONFIG_PATH.is_file():
        return

    try:
        with open(CONFIG_PATH, "r") as f:
            raw_config = json.load(f)
        if not isinstance(raw_config, dict):
            return
        for key, value in raw_config.items():
            _infile_config[key] = value

    except Exception:
        print(format_exc())

_init()


def get_config(key: str, default: Any, checker: Callable[..., bool] | None = None, *checker_args: Any, **checker_kwargs: Any) -> Any:
    if key in _effective_config:
        return _effective_config[key]

    result = _infile_config.get(key, default)
    if not isinstance(result, type(default)):
        result = default
    if checker is not None and checker(result, *checker_args, **checker_kwargs):
        result = default
    _effective_config[key] = result
    return result


def update_config(key: str, value: Any) -> None:
    if key not in _effective_config:
        return
    if not isinstance(value, type(_effective_config[key])):
        return
    _infile_config[key] = value


def save_config() -> None:
    with open(CONFIG_PATH, "w", encoding="utf8") as f:
        f.write(json.dumps(_effective_config, indent=4, ensure_ascii=False))


__all__ = [
    "get_config",
    "update_config",
    "save_config",
]
