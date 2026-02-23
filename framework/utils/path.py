import re


STRICT_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]$')


def is_valid_filename(filename: str) -> bool:
    return re.fullmatch(STRICT_PATTERN, filename) is not None


__all__ = [
    "is_valid_filename",
]
