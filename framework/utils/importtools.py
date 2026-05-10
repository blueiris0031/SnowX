import importlib.util as imp_util
from importlib import import_module
from sys import modules as sys_modules
from types import ModuleType
from typing import Callable, Iterable


def delayed_import(package: str, all_: Iterable[str] = ()) -> Callable[[str], ModuleType]:
    """
    Example:
    # Your __init__.py file

    from framework.utils.importtools import delayed_import

    __all__ = ["aaa", "bbb"]
    __getattr__ = delayed_import(__package__, __all__) # If '__all__' is empty, the module name will not be checked for presence in '__all__'.
    """
    def getattr_(name: str) -> ModuleType:
        if not all_ or name in all_:
            return import_module(f".{name}", package)
        raise AttributeError(f"module '{package}' has no attribute '{name}'")
    return getattr_


def pre_injection_import(name: str, package: str | None = None, **inject_attr) -> ModuleType:
    """
    Before importing the module, inject attributes into it in advance. \n
    Note(1): If the module has been imported, an ImportError will be raised.
    Note(2): The incomed attribute name has not been verified.
    """
    import_path = imp_util.resolve_name(name, package)
    if import_path in sys_modules:
        raise ImportError(f"'{import_path}' already imported")
    module_spec = imp_util.find_spec(import_path)
    if module_spec is None:
        raise ModuleNotFoundError(import_path)
    module = imp_util.module_from_spec(module_spec)
    sys_modules[import_path] = module # In order to make the reflex work normally.
    try:
        for name, attr in inject_attr.items():
            setattr(module, name, attr)
        module_spec.loader.exec_module(module)
        return module
    except BaseException:
        sys_modules.pop(import_path, None)
        raise


__all__ = [
    "delayed_import",
    "pre_injection_import",
]
