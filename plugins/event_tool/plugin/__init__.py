from snowx.api.callback import on_init, on_exit, on_process, on_autorun
from snowx.api.path import get_data_path
from snowx.api.plugin import get_plugin_id
from snowx.plugins.more_trigger import IntervalTrigger
from snowx.plugins.snowx_config import get_config, auto_config
from snowx.types.event import BaseEvent

from .counter import Counter


config = get_config(
    auto_save=auto_config(True),
    save_interval=auto_config(60),
    save_filename=auto_config("count.txt")
)
save_filepath = get_data_path(get_plugin_id()) / config.get("save_filename")


counter = Counter()
counter.load(save_filepath)


if config.get("auto_save"):
    @on_exit
    @on_autorun(trigger=IntervalTrigger(config.get("save_interval")))
    async def _save() -> None:
        counter.save(save_filepath)


@on_process(event_type=BaseEvent)
async def _add_count(_) -> None:
    counter.add()


def get_count() -> int:
    return counter.count


def set_count(count: int) -> None:
    counter.set(count)


__all__ = [
    "get_count",
    "set_count",
]
