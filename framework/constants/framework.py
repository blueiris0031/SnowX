from dataclasses import dataclass
from ..utils.version import Version


@dataclass(frozen=True)
class FrameworkMetadata:
    ID: str = "snowx"
    NAME: str = "SnowX Framework"
    VERSION: Version = Version("1.0.0")


FRAMEWORK_METADATA = FrameworkMetadata()


__all__ = [
    "FRAMEWORK_METADATA",
]
