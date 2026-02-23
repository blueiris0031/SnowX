from enum import Enum


class ProcessStatus(Enum):
    not_running = 0
    running = 1
    run_success = 2
    run_failed = 3


__all__ = [
    "ProcessStatus",
]
