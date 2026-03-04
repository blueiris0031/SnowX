import importlib
from pathlib import Path


_is_mapped: bool = False

def auto_mapper() -> None:
    global _is_mapped
    if _is_mapped:
        return

    for subpath in (
            Path(__file__)
            .parent
            .parent
            .parent
            .iterdir()
    ):
        if not subpath.is_dir():
            continue
        try:
            importlib.import_module(f"{__package__}.{subpath.name}.__mapper__")
        except ImportError:
            pass

    _is_mapped = True


__all__ = ["auto_mapper"]
