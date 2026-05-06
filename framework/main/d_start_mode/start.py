import asyncio
from os import execv
from signal import SIGINT
from sys import executable
from traceback import format_exc

from ...constants.framework import StopState
from ...kernel.manager.manager import framework_manager
from ...state.framework import set_stopping, SNOWX_STOP_STATE, wait_stopping


async def framework_main() -> None:
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(SIGINT, set_stopping, StopState.Stop)

    await framework_manager.start()
    await wait_stopping()
    await framework_manager.stop(SNOWX_STOP_STATE.FORCE)


def main(*_) -> int:
    asyncio.run(framework_main())

    anci_args: list[str] = []
    if SNOWX_STOP_STATE.STATE is StopState.Restart:
        anci_args.append("restart")
    if SNOWX_STOP_STATE.STATE is StopState.Update:
        anci_args.append("update")
        anci_args.append(str(SNOWX_STOP_STATE.UPDATE_PACK))

    if not anci_args:
        return 0
    try:
        execv(executable, ["ancillary.py", *anci_args])
    except Exception:
        print(format_exc())

    return 1


__all__ = [
    "main",
]
