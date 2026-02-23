import importlib
from pathlib import Path


for subpath in Path(__file__).parent.iterdir():
    if not subpath.is_dir():
        continue
    try:
        importlib.import_module(f"{__package__}.{subpath.name}.__mapper__")
    except ImportError:
        pass


from . import kernel


__all__ = ["kernel"]
