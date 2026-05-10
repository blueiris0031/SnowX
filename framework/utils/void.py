"""
NOTE: Never abuse 'Void', as it will cause severe performance degradation in high-frequency invocation scenarios.
"""
from types import MappingProxyType
from typing import Any, Callable


class VoidMeta(type):
    _self_method = lambda self, *_, **__: self
    _fixed_method = lambda value: lambda *_, **__: value

    _rewrote_map = {}
    _special_rewrote_map = {}

    _force_rewrite_methods = {
        "__setattr__": None,
        "__delattr__": None,
        "__call__": None,
    }
    _mcs_protect_list = {
        "__new__",
        "__init__",
        "__call__",
    }

    _instance_map = {}

    def __new__(mcs, name, bases, attrs, **auto_rewrite: Callable | Any | None):
        new_class = super().__new__(mcs, name, bases, attrs)

        direct_getattr = lambda x: type.__getattribute__(mcs, x)

        self_method = direct_getattr("_self_method")
        fixed_method = direct_getattr("_fixed_method")

        rewrote_map = direct_getattr("_rewrote_map")
        rewrote_submap = rewrote_map.setdefault(new_class, {})
        special_rewrote_map = direct_getattr("_special_rewrote_map")
        special_rewrote_submap = special_rewrote_map.setdefault(new_class, {})

        force_rewrite_methods = direct_getattr("_force_rewrite_methods")
        mcs_protect_list = direct_getattr("_mcs_protect_list")

        def gen_special_proxy(name_):
            def proxy(self, *args, **kwargs):
                special_rewrote_submap_ = (
                    special_rewrote_map[self]
                    if self in special_rewrote_map
                    else special_rewrote_map.get(type(self), {})
                )
                if name_ not in special_rewrote_submap_:
                    raise TypeError
                return special_rewrote_submap_[name_](self, *args, **kwargs)
            return proxy

        def getattr_proxy(self, name_, *_, **__):
            rewrote_submap_ = (
                rewrote_map[self]
                if self in rewrote_map
                else rewrote_map.get(type(self), {})
            )
            if name_ not in rewrote_submap_:
                return self
            return lambda *args, **kwargs: rewrote_submap_[name_](self, *args, **kwargs)

        for rewrite_name, rewrite_method in {
            **auto_rewrite,
            **force_rewrite_methods,
            "__getattribute__": getattr_proxy,
        }.items():
            if rewrite_method is None:
                correct_method = self_method
            elif callable(rewrite_method):
                correct_method = rewrite_method
            else:
                correct_method = fixed_method(rewrite_method)

            rewrote_submap[rewrite_name] = correct_method
            if rewrite_name.startswith("__") and rewrite_name.endswith("__"):
                special_rewrote_submap[rewrite_name] = correct_method
                special_proxy = gen_special_proxy(rewrite_name)
                type.__setattr__(new_class, rewrite_name, special_proxy)
                if rewrite_name not in mcs_protect_list:
                    type.__setattr__(mcs, rewrite_name, special_proxy)

        return new_class

    def __call__(cls, *_, **__):
        _instance_map = type.__getattribute__(cls, "_instance_map")
        if cls in _instance_map:
            return _instance_map[cls]
        return _instance_map.setdefault(cls, super().__call__())


class VoidClass(metaclass=VoidMeta):
    pass


def _empty_iterable_next(self) -> None: raise StopIteration(self)

EMPTY_ITERABLE_TEMPLATE = MappingProxyType({"__iter__": None, "__next__": _empty_iterable_next})

INFINITY_ITERABLE_TEMPLATE = MappingProxyType({"__iter__": None, "__next__": None})

SPOOF_PROTOCOL_TEMPLATE = MappingProxyType({**INFINITY_ITERABLE_TEMPLATE, "__contains__": True})

CONTEXT_MANAGER_TEMPLATE = MappingProxyType({"__enter__": None, "__exit__": None})

AWAITABLE_TEMPLATE = MappingProxyType({**EMPTY_ITERABLE_TEMPLATE, "__await__": None})

ASYNC_CONTEXT_MANAGER_TEMPLATE = MappingProxyType({**AWAITABLE_TEMPLATE, "__aenter__": None, "__aexit__": None})


__all__ = [
    "VoidMeta",
    "VoidClass",

    "EMPTY_ITERABLE_TEMPLATE",
    "INFINITY_ITERABLE_TEMPLATE",
    "SPOOF_PROTOCOL_TEMPLATE",
    "CONTEXT_MANAGER_TEMPLATE",
    "AWAITABLE_TEMPLATE",
    "ASYNC_CONTEXT_MANAGER_TEMPLATE",
]
