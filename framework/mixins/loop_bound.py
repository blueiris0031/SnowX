from asyncio import AbstractEventLoop, get_running_loop

from ..types.loop import HasLoopProtocol


class LoopBoundMixin(HasLoopProtocol):
    def __new__(cls, *_, **__):
        instance = super().__new__(cls)
        instance.set_loop()
        return instance

    def set_loop(self, loop: AbstractEventLoop | None = None) -> None:
        if loop is None:
            loop = get_running_loop()
        self._loop = loop

    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop


__all__ = [
    "LoopBoundMixin",
]
