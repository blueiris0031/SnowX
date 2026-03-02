from ..constants.framework_state import StopState
from ..types.framework_state import SnowXState, SnowXStopState


SNOWX_STATE = SnowXState()
SNOWX_STOP_STATE = SnowXStopState()


def get_stop_state() -> SnowXStopState:
    return SNOWX_STOP_STATE


def set_started() -> None:
    SNOWX_STATE.IS_STARTED.set()


def set_stopping(state: StopState = StopState.Stop) -> None:
    SNOWX_STATE.IS_STOPPING.set()
    SNOWX_STOP_STATE.STATE = state


async def wait_started() -> None:
    await SNOWX_STATE.IS_STARTED.wait()


async def wait_stopping() -> None:
    await SNOWX_STATE.IS_STOPPING.wait()


__all__ = [
    "SNOWX_STATE",
    "SNOWX_STOP_STATE",

    "get_stop_state",
    "set_started",
    "set_stopping",
    "wait_started",
    "wait_stopping",
]
