from dataclasses import dataclass

from ..utils.version import Version


@dataclass(frozen=True)
class Metadata:
    ID: str = "snowx"
    NAME: str = "SnowX Framework"
    VERSION: Version = Version("1.0.0")


METADATA = Metadata()


__all__ = [
    "METADATA",
]
