import asyncio
from os import execv
from sys import executable, exit

from framework.constants.framework import FRAMEWORK_METADATA
from framework.kernel.logger import get_logger
from framework.kernel.manager.manager import framework_manager
from framework.state.framework import SNOWX_STOP_STATE, wait_stopping


LOGGER = get_logger("SnowXControlScript")


async def main() -> None:
    await framework_manager.start()
    await wait_stopping()
    await framework_manager.stop(SNOWX_STOP_STATE.FORCE_STOP)


if __name__ == "__main__":
    LOGGER.info(f"Ready to start {FRAMEWORK_METADATA.NAME}.")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.warning("Received the stop signal, ready to stop.")
        LOGGER.warning("This shutdown behavior is unsafe and not recommended when it is not necessary.")
        asyncio.run(framework_manager.stop(SNOWX_STOP_STATE.FORCE_STOP))

    anci_args: list[str] = []
    if SNOWX_STOP_STATE.RESTART:
        anci_args.append("restart")
    if SNOWX_STOP_STATE.UPDATE:
        anci_args.append("update")
        anci_args.append(str(SNOWX_STOP_STATE.UPDATE_PACK))

    if not anci_args:
        exit(0)

    try:
        execv(executable, ["ancillary.py", *anci_args])
    except Exception as e:
        LOGGER.error("Error.", exc_info=e)

    exit(1)
