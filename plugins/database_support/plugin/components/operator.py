from typing import Any, Awaitable, Callable
from inspect import iscoroutinefunction

from ..components.lock import SafeDBOperateLock


_lock = SafeDBOperateLock()


async def set_init() -> None:
    await _lock.set_init()


async def set_close() -> None:
    await _lock.set_close()


async def _operator(coro: Awaitable[Any]) -> Any:
    async with _lock:
        return await coro


def safe_operator(func: Awaitable[Any] | Callable[..., Awaitable[Any]]) -> Awaitable[Any] | Callable[..., Awaitable[Any]]:
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await _operator(func(*args, **kwargs))

    if iscoroutinefunction(func):
        return wrapper
    else:
        return _operator(func)


__all__ = [
    "set_init",
    "set_close",
    "safe_operator",
]
