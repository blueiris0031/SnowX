from ..components.executor import BasicExecutor
from ..types.executor import ExecutorProtocol, HasExecutorProtocol


class ExecutorMixin(HasExecutorProtocol):
    """
    Default executor: BasicExecutor
    """
    
    _executor: ExecutorProtocol = BasicExecutor()

    @property
    def executor(self) -> ExecutorProtocol:
        return self._executor

    def set_executor(self, executor: ExecutorProtocol | None = None) -> None:
        if executor is None:
            executor = type(self)._executor
        if not isinstance(executor, ExecutorProtocol):
            raise TypeError(f"Expected {ExecutorProtocol.__name__}, but got {type(executor).__name__}")
        self._executor = executor


__all__ = [
    "ExecutorMixin",
]
