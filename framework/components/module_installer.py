import sys
from importlib.metadata import distributions

from .command_runner import AsyncCommandRunner
from ..kernel.config import get_config
from ..kernel.logger import get_logger


TIMEOUT: int = get_config("INSTALL_MODULE_TIMEOUT", 60)
TERMINATE_TIMEOUT: int = get_config("INSTALL_MODULE_TERMINATE_TIMEOUT", 10)


_installed_list = []

def _update_installed_list() -> None:
    _installed_list.clear()
    _installed_list.extend(x.metadata["Name"].lower() for x in distributions())

_update_installed_list()


LOGGER = get_logger("ModuleInstaller")


async def install_module(module_name: str) -> bool:
    LOGGER.info(f"<{module_name}>: Prepare to install...")

    runner = AsyncCommandRunner(sys.executable, "-m", "pip", "install", module_name)
    if not await runner.start():
        LOGGER.error(f"<{module_name}>: Failed to install.")
        return False

    if not await runner.wait(TIMEOUT):
        await runner.stop(TERMINATE_TIMEOUT)
        LOGGER.error(f"<{module_name}>: Failed to install.")
        return False

    ret_code, _, stderr = await runner.get_result()
    if ret_code != 0:
        LOGGER.error(f"<{module_name}>: Failed to install.")
        LOGGER.error(f"<{module_name}>: {stderr}")
        return False

    LOGGER.info(f"<{module_name}>: Installed successfully.")
    _update_installed_list()
    return True


async def check_module(module_name: str, auto_install: bool = False) -> bool:
    is_installed = module_name.lower() in _installed_list
    if is_installed:
        return True
    if not auto_install:
        return False

    return await install_module(module_name)


__all__ = [
    "install_module",
    "check_module",
]
