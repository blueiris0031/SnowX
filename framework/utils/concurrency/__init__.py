from ..importtools import delayed_import


__all__ = [
    "asyncio",
    "threading",
]


__getattr__ = delayed_import(__package__, __all__)
