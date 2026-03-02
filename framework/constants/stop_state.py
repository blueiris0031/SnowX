from enum import Enum


class StopState(Enum):
    Stop = 1
    Restart = 2
    Update = 3


__all__ = [
    'StopState',
]
