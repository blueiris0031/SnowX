import sys
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
            ('-' * 128) + '\n'
            'You have entered the interactive mode of the framework.\n' +
            'Please note that only the virtual module mapper will be started in interactive mode, not the framework main program.\n' +
            ('-' * 128)
    )

    try:
        import readline
    except ImportError:
        pass
    console = InteractiveConsole(filename="<snowx_interact>")
    console.interact(
        banner=f"Python {sys.version} on {sys.platform}\n{cprt}\n"
    )
    return 0


__all__ = [
    "main",
]
