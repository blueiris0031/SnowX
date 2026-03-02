from enum import Enum


class StopState(Enum):
    Null = 0
    Stop = 1
    Restart = 2
    Update = 3


__all__ = [
    'StopState',
]
