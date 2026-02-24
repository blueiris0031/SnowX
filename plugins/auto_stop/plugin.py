import asyncio

from snowx.api.callback import on_autorun
from snowx.api.state import wait_started
from snowx.plugins.more_trigger import ResetTrigger
from snowx.plugins.snowx_config import get_config, auto_config
from snowx.types.event import SnowXStopEvent


countdown = max(
    -1,
    get_config(
        count_down=auto_config(-1),
    ).get("count_down")
)


if countdown > -1:
    trigger = ResetTrigger()
    trigger.enable()

    @on_autorun(trigger=trigger)
    async def auto_stop():
        await wait_started()
        await asyncio.sleep(countdown)
        return SnowXStopEvent(force=False)
