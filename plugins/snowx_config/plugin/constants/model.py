from dataclasses import dataclass


@dataclass(frozen=True)
class ModelType:
    NULL: str = "NULL"
    ROOT: str = "ROOT"
    SUB: str = "SUB"

MODEL_TYPE = ModelType()


__all__ = [
    "MODEL_TYPE",
]
