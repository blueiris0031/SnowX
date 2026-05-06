from code import interact
from traceback import format_exc

from ...kernel.vmodule.mapper import auto_mapper


def main(*_) -> int:
    try:
        auto_mapper()
    except Exception:
        print(format_exc())
        return 1

    interact()
    return 0


__all__ = [
    "main",
]
