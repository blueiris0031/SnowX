from ..components.lock import AsyncCompletionLockManager


global_async_completion_lock_manager = AsyncCompletionLockManager()


__all__ = [
    "global_async_completion_lock_manager",
]
