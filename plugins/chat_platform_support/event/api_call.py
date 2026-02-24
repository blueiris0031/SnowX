from dataclasses import dataclass, field

from .base import BaseChatPlatformAPICallEvent
from .message import BaseMessage


@dataclass(frozen=True)
class ChatCallGetUserInfo(BaseChatPlatformAPICallEvent):
    api_name: str = field(init=False, default="get_user_info")
    user_id: str


@dataclass(frozen=True)
class ChatCallGetGroupMemberList(BaseChatPlatformAPICallEvent):
    api_name: str = field(init=False, default="get_group_member_list")
    group_id: str


@dataclass(frozen=True)
class ChatCallSendPrivateMessage(BaseChatPlatformAPICallEvent):
    api_name: str = field(init=False, default="send_private_message")
    user_id: str
    message: tuple[BaseMessage, ...]


@dataclass(frozen=True)
class ChatCallSendGroupMessage(BaseChatPlatformAPICallEvent):
    api_name: str = field(init=False, default="send_group_message")
    group_id: str
    message: tuple[BaseMessage, ...]


__all__ = [
    "ChatCallGetUserInfo",
    "ChatCallGetGroupMemberList",
    "ChatCallSendPrivateMessage",
    "ChatCallSendGroupMessage",
]
