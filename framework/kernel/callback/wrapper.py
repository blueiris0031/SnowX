from ...components.callback.wrapper import (
    EmptyWrapper,
    ProcessWrapper,
    AutorunWrapper,
)


empty_wrapper = EmptyWrapper()
process_wrapper = ProcessWrapper()
autorun_wrapper = AutorunWrapper()


__all__ = [
    "empty_wrapper",
    "process_wrapper",
    "autorun_wrapper",
]
