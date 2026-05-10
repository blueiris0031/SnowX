from threading import Lock


class ExclusiveLock:
    def __init__(self):
        self._lock = Lock()

    def __enter__(self):
        acquired = self._lock.acquire(blocking=False)
        if not acquired:
            raise RuntimeError("Attempt to re-acquire an exclusive lock that is already locked")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()


__all__ = [
    "ExclusiveLock",
]
