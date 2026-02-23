import subprocess
import sys
import re
from os import getcwd, path


def start_core():
    subprocess.Popen(
        " ".join([sys.executable, path.join(getcwd(), "main.py")]),
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
    )

def install(module_list: list[str]) -> None:
    for i in module_list:
        if i.startswith("-") or not re.match(r"^[\w.-]+$", i):
            continue

        try:
            print(f"正在安装<{i}>...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", i])
            print(f"<{i}>安装成功.")

        except subprocess.CalledProcessError:
            print(f"<{i}>安装失败.")


def e(): pass

def r():
    start_core()

def i0():
    if len(sys.argv) < 3:
        return

    install(sys.argv[2:])

def i1():
    i0()
    start_core()


PROCESS = {
    "e": e,
    "r": r,
    "i0": i0,
    "i1": i1,
}


def main():
    if len(sys.argv) < 2:
        return

    func = PROCESS.get(sys.argv[1])
    if func is None:
        return

    func()


if __name__ == "__main__":
    main()
    sys.exit(0)
