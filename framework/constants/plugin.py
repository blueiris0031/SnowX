from enum import StrEnum
from typing import Literal


METADATA_FILENAME: Literal["metadata.json"] = "metadata.json"


class VersionMatchMode(StrEnum):
    NULL = "null"
    MATCH = "match"
    LESS_THAN = "less_than"
    GREATER_THAN = "greater_than"
    IN_RANGE = "in_range"


__all__ = [
    "METADATA_FILENAME",
    "VersionMatchMode",
]
