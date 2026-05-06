from sys import exit
from typing import Any, NoReturn

from . import interact
from . import start
from . import tool


def main(*args: Any) -> NoReturn:
    if not args:
        print("No args provided.")
        exit(1)

    target_name = args[0]

    target_module = globals().get(target_name, None)
    if target_module is None:
        print(f"Unknown arg: <{target_name}>.")
        exit(1)

    target_main = getattr(target_module, "main", None)
    if target_main is None:
        print(f"Unknown arg: <{target_name}>.")
        exit(1)

    exit(target_main(*args[1:]))


__all__ = [
    "main",
]
