from asyncio import AbstractEventLoop, get_running_loop
from concurrent.futures import CancelledError, Future
from threading import Thread, current_thread


def get_loop_thread(loop: AbstractEventLoop) -> Thread:
    """
    Note: If the thread where the EventLoop resides is blocked, this function will also be blocked.
    """
    if not loop.is_running():
        raise RuntimeError("Event loop is not running")

    try:
        if get_running_loop() is loop:
            return current_thread()
    except RuntimeError:
        pass

    def callback(ret_fut: Future[Thread]) -> None:
        try:
            ret_fut.set_result(current_thread())
        except CancelledError:
            pass

    fut: Future[Thread] = Future()
    loop.call_soon_threadsafe(callback, fut)
    return fut.result()


__all__ = [
    "get_loop_thread",
]
