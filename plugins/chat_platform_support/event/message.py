from dataclasses import dataclass, field


@dataclass(frozen=True)
class BaseMessage:
    type: str


@dataclass(frozen=True)
class TextMessage(BaseMessage):
    type: str = field(init=False, default="text")
    text: str

@dataclass(frozen=True)
class MentionMessage(BaseMessage):
    type: str = field(init=False, default="mention")
    user_id: str

@dataclass(frozen=True)
class PictureMessage(BaseMessage):
    type: str = field(init=False, default="picture")
    url: str

@dataclass(frozen=True)
class StickerMessage(BaseMessage):
    type: str = field(init=False, default="sticker")
    url: str


__all__ = [
    "BaseMessage",
    "TextMessage",
    "MentionMessage",
    "PictureMessage",
    "StickerMessage",
]
