import importlib
from pathlib import Path


for name in Path(__file__).parent.iterdir():
    try:
        importlib.import_module(f"{__package__}.{name.name}.__mapper__")
    except ImportError:
        pass


from . import kernel


__all__ = ["kernel"]
