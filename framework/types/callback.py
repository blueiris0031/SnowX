from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class CallbackItem:
    type: str
    identifier: str
    name: str
    func: Callable
    extra_args: tuple[Any, ...]
    extra_kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CallbackResultItem:
    callback: CallbackItem
    is_success: bool
    result: Any


__all__ = [
    "CallbackItem",
    "CallbackResultItem",
]
