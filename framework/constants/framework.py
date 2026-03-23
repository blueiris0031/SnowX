from dataclasses import dataclass
from enum import Enum

from ..utils.version import Version


class StopState(Enum):
    Null = 0
    Stop = 1
    Restart = 2
    Update = 3


@dataclass(frozen=True)
class FrameworkMetadata:
    ID: str = "snowx"
    NAME: str = "SnowX Framework"
    VERSION: Version = Version("0.1.0")


FRAMEWORK_METADATA = FrameworkMetadata()


__all__ = [
    "FRAMEWORK_METADATA",
    "StopState",
]
