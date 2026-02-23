import asyncio
import functools
from typing import Awaitable, Callable

from ..callback.registrar import on_process
from ..logger import get_logger
from ..plugin.api import (
    load_plugin,
    unload_plugin,
    reload_plugin,
    reload_all,
)
from ...state.framework import (
    SNOWX_STATE,
    SNOWX_STOP_STATE,
    set_stopping,
)
from ...types.event import (
    BaseSnowXControlEvent,
    BaseSnowXResultEvent,

    SnowXStopEvent,
    SnowXRestartEvent,
    SnowXUpdateEvent,
    SnowXLoadPluginEvent,
    SnowXLoadPluginResultEvent,
    SnowXUnloadPluginEvent,
    SnowXReloadPluginEvent,
    SnowXReloadPluginResultEvent,
    SnowXReloadAllEvent,
    SnowXReloadAllResultEvent,
)
from ...types.plugin import Metadata


LOGGER = get_logger(SNOWX_STATE.NAME)

__plugin_metadata__ = Metadata(
    id=SNOWX_STATE.ID,
    name=SNOWX_STATE.NAME,
    version=SNOWX_STATE.VERSION,
    entry_point="",
    description="",
    dependent_framework_version=(),
    dependent_plugins=(),
    dependent_modules=(),
)


_safe_lock = asyncio.Lock()

def process_logger(
        func: Callable[[BaseSnowXControlEvent], Awaitable[BaseSnowXResultEvent | None]],
) -> Callable[[BaseSnowXControlEvent], Awaitable[BaseSnowXResultEvent | None]]:
    @functools.wraps(func)
    async def wrapper(event: BaseSnowXControlEvent) -> BaseSnowXResultEvent | None:
        async with _safe_lock:
            LOGGER.info(f"Received event: {event}")
            return await func(event)

    return wrapper


@on_process(event_type=SnowXStopEvent)
@process_logger
async def snowx_stop(event: SnowXStopEvent) -> None:
    if event.force:
        SNOWX_STOP_STATE.FORCE_STOP = True
    set_stopping()


@on_process(event_type=SnowXRestartEvent)
@process_logger
async def snowx_restart(event: SnowXRestartEvent) -> None:
    if event.force:
        SNOWX_STOP_STATE.FORCE_STOP = True
    SNOWX_STOP_STATE.RESTART = True
    set_stopping()


@on_process(event_type=SnowXUpdateEvent)
@process_logger
async def snowx_update(event: SnowXUpdateEvent) -> None:
    if event.force:
        SNOWX_STOP_STATE.FORCE_STOP = True
    SNOWX_STOP_STATE.RESTART = True
    SNOWX_STOP_STATE.UPDATE = True
    SNOWX_STOP_STATE.UPDATE_PACK = event.update_path
    set_stopping()


@on_process(event_type=SnowXLoadPluginEvent)
@process_logger
async def snowx_load_plugin(event: SnowXLoadPluginEvent) -> SnowXLoadPluginResultEvent:
    is_success = await load_plugin(event.identifier)
    return SnowXLoadPluginResultEvent(is_success)


@on_process(event_type=SnowXUnloadPluginEvent)
@process_logger
async def snowx_unload_plugin(event: SnowXUnloadPluginEvent) -> None:
    await unload_plugin(event.identifier)


@on_process(event_type=SnowXReloadPluginEvent)
@process_logger
async def snowx_reload_plugin(event: SnowXReloadPluginEvent) -> SnowXReloadPluginResultEvent:
    return SnowXReloadPluginResultEvent(await reload_plugin(event.identifier))


@on_process(event_type=SnowXReloadAllEvent)
@process_logger
async def snowx_reload_all(_) -> SnowXReloadAllResultEvent:
    await reload_all()
    return SnowXReloadAllResultEvent()


__all__ = []
