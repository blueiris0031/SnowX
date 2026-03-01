from sys import argv as sys_argv, exit as sys_exit
from traceback import format_exc
from typing import NoReturn, Callable
from importlib import import_module


def _run() -> int:
    tool_name = sys_argv[1]
    try:
        tool = import_module(f"tools.{tool_name}")
    except ImportError:
        print(f"Unknown tool: <{tool_name}>.")
        return 1

    if not hasattr(tool, "run"):
        print(f"Unknown tool: <{tool_name}>.")
        return 1
    tool_func: Callable[..., int] = getattr(tool, "run")
    if not callable(tool_func):
        print(f"Unknown tool: <{tool_name}>.")
        return 1

    try:
        return tool_func(*sys_argv[3:])
    except Exception:
        print(f"Tool run failed: <{tool_name}>.>")
        print(format_exc())
        return 1


def run() -> NoReturn:
    sys_exit(_run())


__all__ = ["run"]
