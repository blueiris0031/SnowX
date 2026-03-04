import asyncio
from os import execv
from signal import SIGINT
from sys import executable, exit
from traceback import format_exc
from typing import NoReturn

from .kernel.manager.manager import framework_manager
from .state.framework import set_stopping, SNOWX_STOP_STATE, wait_stopping


async def framework_main() -> None:
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(SIGINT, set_stopping)

    await framework_manager.start()
    await wait_stopping()
    await framework_manager.stop(SNOWX_STOP_STATE.FORCE_STOP)


def main() -> NoReturn:
    asyncio.run(framework_main())

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
    except Exception:
        print(format_exc())
    exit(1)


__all__ = [
    "main",
]
