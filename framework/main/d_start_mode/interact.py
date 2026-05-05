from code import interact
from sys import exit
from traceback import format_exc
from typing import NoReturn

from ...kernel.vmodule.mapper import auto_mapper


def main(*_) -> NoReturn:
    try:
        auto_mapper()
    except Exception:
        print(format_exc())
        exit(1)

    interact()
    exit(0)


__all__ = [
    "main",
]

