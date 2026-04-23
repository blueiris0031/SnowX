import asyncio

from snowx.api.callback import on_autorun
from snowx.api.state import wait_started
from snowx.plugins.more_trigger import ResetTrigger
from snowx.plugins.snowx_config import BaseConfigRootModel, gen_root_model_kwargs
from snowx.types.event import SnowXStopEvent


class AutoStopConfig(BaseConfigRootModel, **gen_root_model_kwargs("auto_stop")):
    count_down: int = -1


config = AutoStopConfig()


countdown = max(
    -1,
    config.count_down,
)


if countdown > -1:
    trigger = ResetTrigger()
    trigger.enable()

    @on_autorun(trigger=trigger)
    async def auto_stop():
        await wait_started()
        await asyncio.sleep(countdown)
        return SnowXStopEvent(force=False)


__all__ = []
