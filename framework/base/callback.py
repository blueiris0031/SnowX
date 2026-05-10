from abc import abstractmethod
from typing import Any, Awaitable, Callable, Iterable, Literal, Self, Type

from .executor import BaseExecutor
from ..types.callback import CallbackItem
from ..utils.worker import BaseProducerConsumerWorker


class BaseSchedulerItem(BaseProducerConsumerWorker):
    _scheduler_item_cls_map: dict[str, Type["BaseSchedulerItem"]] = {}

    @classmethod
    def add_scheduler_item_cls(
            cls,
            callback_type: str,
            item_cls: Type["BaseSchedulerItem"],
    ):
        cls._scheduler_item_cls_map[callback_type] = item_cls

    @classmethod
    def get_scheduler_item_cls(cls, callback_type: str) -> Type["BaseSchedulerItem"]:
        if callback_type not in cls._scheduler_item_cls_map:
            raise LookupError(f"scheduler item does not exist: {callback_type}")
        return cls._scheduler_item_cls_map[callback_type]

    @classmethod
    def del_scheduler_item_cls(cls, callback_type: str) -> None:
        cls._scheduler_item_cls_map.pop(callback_type, None)

    def __init_subclass__(cls, callback_type: str | None = None) -> None:
        if callback_type is None:
            return
        cls.add_scheduler_item_cls(callback_type, cls)

    def __init__(
            self,
            callbacks: Iterable[CallbackItem],
            executor: BaseExecutor,
            consumer_queue_maxsize: int = 0,
            consumer_callback: Callable[[...], None] | None = None,
            **extension_method: Callable[[Self, ...], Any],
    ):
        super().__init__(consumer_queue_maxsize, consumer_callback)
        self._callbacks = tuple(callbacks)
        self._executor = executor

        self._wrapped_callbacks: tuple[tuple[CallbackItem, Callable[..., Awaitable[tuple[Literal[True], Any] | tuple[Literal[False], Exception]]]], ...] | None = None

        self._extension_method_map: dict[str, Callable[[Self, ...], Any]] = {}
        for name, method in extension_method.items():
            self.add_extension_method(name, method)

    @property
    def executor(self) -> BaseExecutor:
        """
        Pre-generated attributes.
        """
        return self._executor

    @property
    def callbacks(self) -> tuple[CallbackItem, ...]:
        """
        Pre-generated attributes.
        """
        return self._callbacks

    @property
    def wrapped_callbacks(self) -> tuple[
        tuple[
            CallbackItem,
            Callable[
                ..., Awaitable[tuple[Literal[True], Any] | tuple[Literal[False], Exception]]
            ]
        ], ...
    ]:
        """
        Pre-generated attributes(Lazy generation).
        """
        if self._wrapped_callbacks:
            return self._wrapped_callbacks

        self._wrapped_callbacks = tuple(
            (
                callback,
                self._executor(callback.func, **callback.extra_kwargs)
            ) for callback in self.callbacks
        )
        return self._wrapped_callbacks

    def add_extension_method(
            self,
            name: str,
            method: Callable[[Self, ...], Any],
    ) -> None:
        if hasattr(self, name):
            raise AttributeError(f"'{name}' already defined")
        self._extension_method_map[name] = lambda *args, **kwargs: method(self, *args, **kwargs)

    def get_extension_method(
            self,
            name: str,
    ) -> Callable[[Self, ...], Any]:
        if name not in self._extension_method_map:
            raise LookupError(f"'{name}' does not exist")
        return self._extension_method_map[name]

    def del_extension_method(
            self,
            name: str,
    ) -> None:
        self._extension_method_map.pop(name, None)

    def __getattr__(self, name: str) -> Any:
        return self.get_extension_method(name)

    @abstractmethod
    async def producer(self) -> Any | None:
        pass

    @abstractmethod
    async def consumer(self, data: Any) -> Any:
        pass


def get_scheduler_item_cls(callback_type: str) -> Type["BaseSchedulerItem"]:
    return BaseSchedulerItem.get_scheduler_item_cls(callback_type)


__all__ = [
    "BaseSchedulerItem",
    "get_scheduler_item_cls",
]
