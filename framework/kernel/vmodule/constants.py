from dataclasses import dataclass


@dataclass(frozen=True)
class VModuleRootPath:
    ROOT: str = "snowx"

VMODULE_ROOT_PATH = VModuleRootPath()


@dataclass(frozen=True)
class VModuleSubrootPath:
    API: str = "api"
    BASE: str = "base"
    COMPONENTS: str = "components"
    CONSTANTS: str = "constants"
    ERROR: str = "error"
    KERNEL: str = "kernel"
    PLUGINS: str = "plugins"
    STATE: str = "state"
    TYPES: str = "types"
    UTILS: str = "utils"

VMODULE_SUBROOT_PATH = VModuleSubrootPath()


__all__ = [
    "VMODULE_ROOT_PATH",
    "VMODULE_SUBROOT_PATH",
]
