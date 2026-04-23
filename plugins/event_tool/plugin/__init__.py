from snowx.api.callback import on_init, on_exit, on_process, on_autorun
from snowx.api.path import get_data_path
from snowx.api.plugin import get_plugin_id
from snowx.plugins.more_trigger import IntervalTrigger
from snowx.plugins.snowx_config import BaseConfigRootModel, gen_root_model_kwargs
from snowx.types.event import BaseEvent

from .counter import Counter


class EventToolConfig(BaseConfigRootModel, **gen_root_model_kwargs("event_tool")):
    auto_save: bool = True
    save_interval: int = 60
    save_filename: str = "event_count.txt"


config = EventToolConfig()
save_filepath = get_data_path(get_plugin_id()) / config.save_filename


counter = Counter()
counter.load(save_filepath)


if config.auto_save:
    @on_exit
    @on_autorun(trigger=IntervalTrigger(config.save_interval))
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
