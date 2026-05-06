from typing import Any

from . import mapping


def main(*args: Any) -> int:
    if not args:
        print("No args provided.")
        exit(1)

    target_name = args[0]

    target_module = globals().get(target_name, None)
    if target_module is None:
        print(f"Unknown arg: <{target_name}>.")
        return 1

    target_main = getattr(target_module, "main", None)
    if target_main is None:
        print(f"Unknown arg: <{target_name}>.")
        return 1

    return target_main(*args[1:])


__all__ = [
    "main",
]
