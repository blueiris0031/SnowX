from traceback import format_exc

from ...kernel.vmodule.mapper import auto_mapper


def main(*_) -> int:
    try:
        auto_mapper()
        return 0
    except Exception:
        print(format_exc())
        return 1


__all__ = [
    "main",
]
