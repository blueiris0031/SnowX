import asyncio
from dataclasses import dataclass
from pathlib import Path

from ..utils.version import Version


@dataclass(frozen=True)
class SnowXState:
    IS_STARTED: asyncio.Event = asyncio.Event()
    IS_STOPPING: asyncio.Event = asyncio.Event()


@dataclass
class SnowXStopState:
    FORCE_STOP: bool = False
    RESTART: bool = False
    UPDATE: bool = False
    UPDATE_PACK: Path | None = None


SNOWX_STATE = SnowXState()
SNOWX_STOP_STATE = SnowXStopState()


def set_started() -> None:
    SNOWX_STATE.IS_STARTED.set()


def set_stopping() -> None:
    SNOWX_STATE.IS_STOPPING.set()


async def wait_started() -> None:
    await SNOWX_STATE.IS_STARTED.wait()


async def wait_stopping() -> None:
    await SNOWX_STATE.IS_STOPPING.wait()


__all__ = [
    "SNOWX_STATE",
    "SNOWX_STOP_STATE",

    "set_started",
    "set_stopping",
    "wait_started",
    "wait_stopping",
]
