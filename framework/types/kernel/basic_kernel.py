from abc import abstractmethod
from typing import Callable, Coroutine, Protocol, runtime_checkable

from ..executor import HasExecutorProtocol
from ..lifecycle import LifeCycleProtocol
from ..logging import HasLoggerProtocol


_TASK_FUNC = Callable[[], Coroutine[None, None, None] | None]


@runtime_checkable
class BasicKernelProtocol(LifeCycleProtocol, HasExecutorProtocol, HasLoggerProtocol, Protocol):
    @abstractmethod
    def submit_task(self, task: _TASK_FUNC, critical: bool = False) -> None:
        """
        Note: Only tasks related to kernel state are permitted to be submitted; tasks related to business logic are strictly prohibited.
        """
        pass

    @abstractmethod
    def submit_stop_callback(self, task: _TASK_FUNC) -> None:
        """
        Note: If the submitted callback is blocked, it may cause a deadlock in 'BasicKernel'.
        """
        pass

    @abstractmethod
    def submit_panic_callback(self, task: _TASK_FUNC) -> None:
        """
        Note: If the submitted callback is blocked, it may cause a deadlock in 'BasicKernel'.
        """
        pass

    @abstractmethod
    async def main(self) -> None:
        """
        This function should not be called externally.
        """
        pass


__all__ = [
    "BasicKernelProtocol",
]
