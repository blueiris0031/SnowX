import asyncio
from dataclasses import dataclass
from pathlib import Path

from ..constants.framework import StopState


@dataclass(frozen=True)
class SnowXState:
    IS_STARTED: asyncio.Event = asyncio.Event()
    IS_STOPPING: asyncio.Event = asyncio.Event()


@dataclass
class SnowXStopState:
    STATE: StopState = StopState.Null
    FORCE: bool = False
    UPDATE_PACK: Path | None = None


__all__ = [
    "SnowXState",
    "SnowXStopState",
]
