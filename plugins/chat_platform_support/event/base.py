from dataclasses import dataclass

from snowx.types.event import BaseEvent


@dataclass(frozen=True)
class BaseChatPlatformSupportEvent(BaseEvent):
    platform_id: str


@dataclass(frozen=True)
class BaseChatPlatformEvent(BaseChatPlatformSupportEvent):
    event_type: str


@dataclass(frozen=True)
class BaseChatPlatformAPICallEvent(BaseChatPlatformSupportEvent):
    api_name: str
    call_id: str


@dataclass(frozen=True)
class BaseChatPlatformAPICallResponseEvent(BaseChatPlatformSupportEvent):
    api_name: str
    call_id: str


__all__ = [
    "BaseChatPlatformSupportEvent",
    "BaseChatPlatformEvent",
    "BaseChatPlatformAPICallEvent",
    "BaseChatPlatformAPICallResponseEvent",
]
