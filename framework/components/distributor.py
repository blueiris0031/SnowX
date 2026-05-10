import asyncio
import warnings
from traceback import print_exc
from typing import Callable, Hashable, Type, TypeVar

from ..utils.queue import TypedAsyncQueue
from ..utils.worker import BaseProducerConsumerWorker


_O = TypeVar("_O", bound=object)


class TypedObjectDistributor(BaseProducerConsumerWorker):
    def __init__(
            self,
            object_bus_maxsize: int = 0,
            distributor_queue_maxsize: int = 0,
            distributor_buffer_maxsize: int = 0,
    ):
        """
        :param object_bus_maxsize: Maxsize of object bus.
        :param distributor_queue_maxsize: Maxsize of distributor queue.
        :param distributor_buffer_maxsize: Maxsize of distributor buffer. When the distributor queue is full, this parameter determines how many coroutines can be waiting for the distribution object.
        """
        super().__init__(distributor_buffer_maxsize)

        self._object_bus: TypedAsyncQueue[object] = TypedAsyncQueue(
            object,
            strict_mode=False,
            maxsize=object_bus_maxsize,
        )
        self._distributor_queue_maxsize = distributor_queue_maxsize

        self._distributor_map: dict[Hashable, tuple[TypedAsyncQueue[object], Callable[[Type[object]], bool]]] = {}
        self._matched_type_cache: dict[Type, tuple[TypedAsyncQueue[object], ...]] = {}

    def _get_matched_distributor(self, obj: _O) -> tuple[TypedAsyncQueue[_O], ...]:
        obj_type: Type[_O] = type(obj)
        if obj_type in self._matched_type_cache:
            return self._matched_type_cache[obj_type]

        new_cache: list[TypedAsyncQueue[_O]] = []
        for symbol, distributor_inf in self._distributor_map.items():
            try:
                if distributor_inf[1](obj_type):
                    new_cache.append(distributor_inf[0])
            except Exception:
                warnings.warn(f"An abnormality in the type checker with symbol <{symbol}>, skip", RuntimeWarning)
                print_exc()

        return self._matched_type_cache.setdefault(obj_type, tuple(new_cache))

    def _clear_type_cache(self) -> None:
        self._matched_type_cache.clear()

    async def producer(self) -> object:
        obj = await self._object_bus.get()
        self._object_bus.task_done()
        return obj

    async def consumer(self, obj: object) -> None:
        distributors = self._get_matched_distributor(obj)
        if not distributors:
            return
        await asyncio.gather(*(queue.auto_put(obj) for queue in distributors))

    @staticmethod
    def _gen_checker(obj_types: tuple[Type[_O], ...], strict_mode: bool) -> Callable[[Type[_O]], bool]:
        if strict_mode:
            obj_types_set = set(obj_types)
            return lambda type_: type_ in obj_types_set
        else:
            return lambda type_: issubclass(type_, obj_types)

    def subscribe(
            self,
            symbol: Hashable,
            *obj_types: Type[_O],
            update_distributor: bool = False,
            custom_checker: Callable[[Type[object]], bool] | None = None,
            strict_mode: bool = False,
    ) -> TypedAsyncQueue[_O]:
        """
        Subscribe to a distributor.
        Note: Due to some internal implementation changes, additional object types are no longer supported when using the existing symbol subscription distributor.
        :param symbol: The symbol of the distributor. This parameter will ensure that the same distributor instance is obtained when the same symbol is subscribed.
        :param obj_types: Object types that need to be matched.
        :param update_distributor: If this parameter is True, the current distributor parameter will be updated to the distributor corresponding to the symbol, otherwise it will remain unchanged. Note: If this symbol has not been subscribed to the distributor before, this parameter will not have any practical effect.
        :param custom_checker: If this parameter is not None, use it as a type checker and ignore other parameters related to type checking.
        :param strict_mode: This is a parameter related to type checking. If this parameter is True, it will only match objects with exactly the same type, otherwise it will match the subclass.
        :return: Object distributor.
        """
        if symbol not in self._distributor_map:
            self._distributor_map[symbol] = (
                TypedAsyncQueue(object, strict_mode=False, maxsize=self._distributor_queue_maxsize),
                custom_checker or self._gen_checker(obj_types, strict_mode),
            )
            self._clear_type_cache()

        distributor, _ = self._distributor_map[symbol]
        if not update_distributor:
            return distributor

        self._distributor_map[symbol] = (distributor, custom_checker or self._gen_checker(obj_types, strict_mode))
        self._clear_type_cache()
        return distributor

    def unsubscribe(self, symbol: Hashable) -> None:
        """
        Unsubscribe to a distributor.
        :param symbol: The symbol of the distributor that needs to be unsubscribed
        :return: None.
        """
        self._distributor_map.pop(symbol, None)
        self._clear_type_cache()

    async def put_object(self, obj: tuple[_O, ...] | list[_O] | set[_O] | _O) -> None:
        """
        Put the object into the object bus。
        :param obj: The object to be put into the object bus.
        :return: None.
        """
        await self._object_bus.auto_put(obj)


__all__ = [
    "TypedObjectDistributor",
]
