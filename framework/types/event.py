from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BaseEvent:
    pass


@dataclass(frozen=True)
class BaseSnowXEvent(BaseEvent):
    pass


@dataclass(frozen=True)
class BaseSnowXControlEvent(BaseSnowXEvent):
    pass


@dataclass(frozen=True)
class BaseSnowXResultEvent(BaseSnowXEvent):
    pass


@dataclass(frozen=True)
class SnowXStopEvent(BaseSnowXControlEvent):
    force: bool


@dataclass(frozen=True)
class SnowXRestartEvent(BaseSnowXControlEvent):
    force: bool


@dataclass(frozen=True)
class SnowXUpdateEvent(BaseSnowXControlEvent):
    force: bool
    update_path: Path = Path.cwd() / "update.zip"


@dataclass(frozen=True)
class SnowXLoadPluginEvent(BaseSnowXControlEvent):
    identifier: str


@dataclass(frozen=True)
class SnowXLoadPluginResultEvent(BaseSnowXResultEvent):
    is_success: bool


@dataclass(frozen=True)
class SnowXUnloadPluginEvent(BaseSnowXControlEvent):
    identifier: str


@dataclass(frozen=True)
class SnowXReloadPluginEvent(BaseSnowXControlEvent):
    identifier: str


@dataclass(frozen=True)
class SnowXReloadPluginResultEvent(BaseSnowXResultEvent):
    is_success: bool


@dataclass(frozen=True)
class SnowXReloadAllEvent(BaseSnowXControlEvent):
    pass


@dataclass(frozen=True)
class SnowXReloadAllResultEvent(BaseSnowXResultEvent):
    pass


__all__ = [
    "BaseEvent",

    "BaseSnowXEvent",
    "BaseSnowXControlEvent",
    "BaseSnowXResultEvent",

    "SnowXStopEvent",
    "SnowXRestartEvent",
    "SnowXUpdateEvent",

    "SnowXLoadPluginEvent",
    "SnowXLoadPluginResultEvent",
    "SnowXUnloadPluginEvent",
    "SnowXReloadPluginEvent",
    "SnowXReloadPluginResultEvent",
    "SnowXReloadAllEvent",
    "SnowXReloadAllResultEvent",
]
