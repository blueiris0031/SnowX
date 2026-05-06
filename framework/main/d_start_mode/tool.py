from traceback import format_exc
from typing import Callable
from importlib import import_module


def main(*args) -> int:
    if not args:
        print("There are no specified running tools.")
        return 1

    tool_name = args[0]
    try:
        tool = import_module(f"tools.{tool_name}")
    except ImportError:
        print(f"Unknown tool: <{tool_name}>")
        return 1

    if not hasattr(tool, "run"):
        print(f"Unknown tool: <{tool_name}>")
        return 1

    tool_func: Callable[..., int] = getattr(tool, "main")
    if not callable(tool_func):
        print(f"Unknown tool: <{tool_name}>")
        return 1

    try:
        return tool_func(args[1:])
    except Exception:
        print(f"An exception occurs when the tool is running: <{tool_name}>")
        print(format_exc())
        return 1


__all__ = [
    "main",
]
