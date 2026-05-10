from enum import StrEnum


class ModulePath(StrEnum):
    ROOT = "snowx"
    API = f"{ROOT}.api"
    BASE = f"{ROOT}.base"
    COMPONENTS = f"{ROOT}.components"
    CONSTANTS = f"{ROOT}.constants"
    ERROR = f"{ROOT}.error"
    KERNEL = f"{ROOT}.kernel"
    PLUGINS = f"{ROOT}.plugins"
    TYPES = f"{ROOT}.types"
    UTILS = f"{ROOT}.utils"


__all__ = [
    "ModulePath",
]
