from dataclasses import dataclass, field

from .base import BaseChatPlatformEvent
from .message import BaseMessage


@dataclass(frozen=True)
class ChatPrivateMessageEvent(BaseChatPlatformEvent):
    event_type: str = field(init=False, default="private_message")

    user_id: str
    message_id: str
    message: tuple[BaseMessage, ...]

@dataclass(frozen=True)
class ChatGroupMessageEvent(BaseChatPlatformEvent):
    event_type: str = field(init=False, default="group_message")

    group_id: str
    user_id: str
    message_id: str
    message: tuple[BaseMessage, ...]


__all__ = [
    "ChatPrivateMessageEvent",
    "ChatGroupMessageEvent",
]
