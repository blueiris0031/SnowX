import asyncio
from typing import Awaitable, Any


async def _executor(*coro_or_future: Awaitable[Any], return_exceptions: bool = False) -> tuple[Any, ...]:
    results: list[Any] = []

    for awaitable in coro_or_future:
        if not return_exceptions:
            results.append(await awaitable)
            continue

        try:
            results.append(await awaitable)
        except asyncio.CancelledError:
            raise asyncio.CancelledError
        except Exception as e:
            results.append(e)

    return tuple(results)


def serial_executor(*coro_or_future: Awaitable[Any], return_exceptions: bool = False) -> Awaitable[tuple[Any, ...]]:
    return asyncio.create_task(_executor(*coro_or_future, return_exceptions=return_exceptions))


__all__ = [
    "serial_executor",
]
