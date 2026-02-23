from snowx.api.callback import on_init, on_exit, on_process, on_autorun
from snowx.api.path import get_data_path
from snowx.plugins.more_trigger import IntervalTrigger
from snowx.plugins.snowx_config import get_config, auto_config
from snowx.types.event import BaseEvent


from .counter import Counter


_config = get_config(
    auto_save=auto_config(True),
    save_interval=auto_config(60),
    save_filename=auto_config("count.txt")
)
_save_filepath = get_data_path(__plugin_metadata__.id) / _config.get("save_filename")


_counter = Counter()
_counter.load(_save_filepath)


if _config.get("auto_save"):
    @on_exit
    @on_autorun(trigger=IntervalTrigger(_config.get("save_interval")))
    async def _save() -> None:
        _counter.save(_save_filepath)


@on_process(event_type=BaseEvent)
async def _add_count(_) -> None:
    _counter.add()


def get_count() -> int:
    return _counter.count


def set_count(count: int) -> None:
    _counter.set(count)


__all__ = [
    "get_count",
    "set_count",
]
