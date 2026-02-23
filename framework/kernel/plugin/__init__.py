from . import inject_load
from ...utils.delayed_import import delayed_import


__all__ = [
    "api",
    "deps",
    "importer",
    "info",
    "manager",
    "metadata",
]


__getattr__ = delayed_import(__all__, __package__)
