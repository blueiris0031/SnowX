from dataclasses import dataclass, field

from .base import BaseChatPlatformAPICallResponseEvent


@dataclass(frozen=True)
class ChatUserInfoResponseEvent(BaseChatPlatformAPICallResponseEvent):
    api_name: str = field(init=False, default="user_info")

    user_id: str
    user_nickname: str

@dataclass(frozen=True)
class ChatGroupMemberListResponseEvent(BaseChatPlatformAPICallResponseEvent):
    api_name: str = field(init=False, default="group_member_list")

    group_id: str
    member_list: tuple[str, ...]


__all__ = [
    "ChatUserInfoResponseEvent",
    "ChatGroupMemberListResponseEvent",
]