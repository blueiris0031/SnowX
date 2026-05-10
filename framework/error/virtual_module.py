class ModuleExistsError(Exception):
    pass


class ObjectExistsError(Exception):
    pass


class InvalidModuleNameError(Exception):
    pass


__all__ = [
    "ModuleExistsError",
    "ObjectExistsError",
    "InvalidModuleNameError",
]
