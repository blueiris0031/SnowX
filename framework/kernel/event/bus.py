from ..config import get_config
from ...types.event import BaseEvent
from ...utils.queue import TypedAsyncQueue


global_event_bus = TypedAsyncQueue(BaseEvent, get_config("EVENT_BUS_MAXSIZE", 1024))


__all__ = [
    "global_event_bus",
]
