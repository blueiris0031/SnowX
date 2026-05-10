import __main__
import re
from pathlib import Path


_STRICT_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]$')


def is_valid_name(filename: str) -> bool:
    """
    Note: This check is relatively strict.
    """
    return re.fullmatch(_STRICT_PATTERN, filename) is not None


def get_main_path() -> Path:
    main_path = __main__.__file__
    if main_path is None:
        raise RuntimeError("Main program file does not exist")
    return Path(main_path).resolve()


def get_root_path() -> Path:
    return get_main_path().parent


def get_src_path() -> Path:
    src_path = get_root_path() / __name__.split(".", 1)[0]
    if not src_path.is_dir():
        raise RuntimeError("Failed to retrieve the source path")
    return src_path


__all__ = [
    "is_valid_name",
    "get_main_path",
    "get_root_path",
    "get_src_path",
]
