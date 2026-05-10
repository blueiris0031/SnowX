from enum import Enum


class RunningStatus(Enum):
    Stopped = 0
    Starting = 1
    Running = 2
    Stopping = 3


class StopType(Enum):
    Normal = 0
    Force = 1


__all__ = [
    "RunningStatus",
    "StopType",
]
