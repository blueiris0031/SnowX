from typing import Any, NoReturn
from sys import exit

from . import interact
from . import start


def main(*args: Any) -> NoReturn:
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
