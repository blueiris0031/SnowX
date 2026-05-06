import __main__
import re
from pathlib import Path


STRICT_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]$')


def is_valid_filename(filename: str) -> bool:
    return re.fullmatch(STRICT_PATTERN, filename) is not None


def get_main_path() -> Path:
    main_path = __main__.__file__
    if main_path is None:
        raise RuntimeError("Main program file does not exist")

    return Path(main_path).resolve()


__all__ = [
    "is_valid_filename",
    "get_main_path",
]
