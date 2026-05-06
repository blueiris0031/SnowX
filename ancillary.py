from os import execv
from pathlib import Path
from sys import argv as sys_argv, executable
from typing import Any


def start_main(*args: Any):
    execv(executable, [str(Path.cwd() / "main.py"), *args])


def update(update_pack: str, *args: Any):
    print(update_pack)
    start_main(*args)


def main():
    args = sys_argv[1:]

    if not args:
        return

    process = args[0]
    s_args = args[1:]

    match process:
        case "restart":
            start_main(*s_args)
        case "update":
            update(*s_args)


if __name__ == "__main__":
    main()
