import sys
from shutil import get_terminal_size
from code import InteractiveConsole
from traceback import format_exc

from ...kernel.vmodule.mapper import auto_mapper


def main(*_) -> int:
    try:
        auto_mapper()
    except Exception:
        print(format_exc())
        return 1

    cprt = (
            'Type "help", "copyright", "credits" or "license" for more information.\n\n' +
            ((get_terminal_size().columns // 2) * "-") + '\n'
            'You have entered the interactive mode of the framework.\n' +
            'Please note that only the virtual module mapper will be started in interactive mode, not the framework main program.\n' +
            ((get_terminal_size().columns // 2) * "-")
    )

    try:
        import readline
    except ImportError:
        pass
    console = InteractiveConsole(filename="<snowx_interact>")
    try:
        console.interact(f"Python {sys.version} on {sys.platform}\n{cprt}\n")
    except SystemExit:
        pass

    print("Exiting interactive mode...")
    return 0


__all__ = [
    "main",
]
