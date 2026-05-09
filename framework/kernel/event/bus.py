from ..config import config_manager
from ...types.event import BaseEvent
from ...utils.queue import TypedAsyncQueue


global_event_bus = TypedAsyncQueue(BaseEvent, config_manager.get_config("EVENT_BUS_MAXSIZE", 1024))


__all__ = [
    "global_event_bus",
]
