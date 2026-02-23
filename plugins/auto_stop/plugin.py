from snowx.api.callback import on_autorun
from snowx.api.state import wait_started
from snowx.plugins.more_trigger import IntervalTrigger
from snowx.plugins.snowx_config import get_config, auto_config
from snowx.types.event import SnowXStopEvent


countdown = get_config(count_down=auto_config(-1)).get("count_down")
countdown = max(-1, countdown)


if countdown > -1:
    @on_autorun(trigger=IntervalTrigger(countdown))
    async def auto_stop():
        await wait_started()
        return SnowXStopEvent(force=False)
