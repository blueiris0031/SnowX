import importlib
from pathlib import Path


_is_mapped: bool = False

def auto_mapper() -> None:
    global _is_mapped
    if _is_mapped:
        return

    base_path = Path(__file__).parent.parent.parent
    for subpath in base_path.iterdir():
        if not subpath.is_dir():
            continue
        try:
            importlib.import_module(f"{base_path.name}.{subpath.name}.__mapper__")
        except ImportError:
            pass

    _is_mapped = True


__all__ = ["auto_mapper"]
