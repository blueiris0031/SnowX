"""
Note: The callable returned by 'singleton_decorator' is not the decorated class.
"""
from typing import Any, Callable, Type, TypeVar

from .paramtools import get_params_generator


_I = TypeVar("_I")


def singleton_decorator(cls: Type[_I]) -> Callable[..., _I]:
    instance = None
    def init(*args, **kwargs) -> _I:
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance
    return init


def configured_singleton_decorator(
        cls: Type[_I] | None = None,
        params_generator: Callable[..., tuple[tuple[Any, ...], dict[str, Any]]] | None = None,
) -> Callable[..., _I] | Callable[[_I], Callable[..., _I]]:
    """
    It is recommended to use the 'get_params_generator' function inside 'utils.paramtools' to generate 'params_generator'.
    """
    params_gen = params_generator or get_params_generator("ignore", (), "ignore", {})

    base_singleton_init: Callable[..., _I] | None = None
    def init(*args, **kwargs) -> _I:
        nonlocal base_singleton_init
        if base_singleton_init is None:
            raise RuntimeError("'base_singleton_init' is None")
        c_args, c_kwargs = params_gen(*args, **kwargs)
        return base_singleton_init(*c_args, **c_kwargs)

    def init_singleton(cls_: Type[_I]) -> Callable[..., _I]:
        nonlocal base_singleton_init
        base_singleton_init = singleton_decorator(cls_)
        return init

    if cls is None:
        return init_singleton
    return init_singleton(cls)


class SingletonMeta(type):
    _s_instance_map: dict[Type[Any], Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls in cls._s_instance_map:
            return cls._s_instance_map[cls]
        return cls._s_instance_map.setdefault(cls, super().__call__(*args, **kwargs))


class ConfiguredSingletonMeta(SingletonMeta):
    """
    It is recommended to use the 'get_params_generator' function inside 'utils.paramtools' to generate 'params_generator'.
    """
    _c_params_generator_map: dict[Type, Callable[..., tuple[tuple[Any, ...], dict[str, Any]]]] = {}

    def __new__(
            mcs,
            name: str,
            bases: tuple[Type],
            attrs: dict[str, Any],
            params_generator: Callable[..., tuple[tuple[Any, ...], dict[str, Any]]] | None = None,
            **kwargs,
    ):
        new_class = super().__new__(mcs, name, bases, attrs, **kwargs)
        mcs._c_params_generator_map[new_class] = params_generator or get_params_generator("ignore", (), "ignore", {})
        return new_class

    def __call__(cls, *args, **kwargs):
        c_args, c_kwargs = cls._c_params_generator_map.get(cls)(*args, **kwargs)
        return super().__call__(*c_args, **c_kwargs)


class SingletonClass:
    """
    When using this class, please override the '_real_init' method.
    """
    def __new__(cls, *args, **kwargs):
        if hasattr(cls, "_instance"):
            return getattr(cls, "_instance")[0]
        cls._instance = (instance := super().__new__(cls), False)
        return instance

    def __init__(self, *args, **kwargs):
        instance, is_init = self._instance
        if is_init:
            return
        self._real_init(*args, **kwargs)
        type(self)._instance = instance, True

    def _real_init(self, *args, **kwargs):
        pass


__all__ = [
    "singleton_decorator",
    "configured_singleton_decorator",
    "SingletonMeta",
    "ConfiguredSingletonMeta",
    "SingletonClass",
]
