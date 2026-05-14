from typing import Any, Callable


class VoidMeta(type):
    _void_instance_map = {}
    _void_rewrote_map = {}
    _void_special_rewrote_map = {}

    _void_none_method = lambda *_, **__: None
    _void_self_method = lambda cls_or_self, *_, **__: cls_or_self
    _void_custom_method = lambda value: lambda *_, **__: value
    _void_force_rewrite_methods = {
        "__setattr__": False,
        "__delattr__": False,
        "__call__": True,
    }
    _void_mcs_protect_list = {
        "__new__",
        "__init__",
        "__call__",
    }

    def __new__(mcs, name, bases, attrs, **auto_rewrite: bool | Callable[..., Any] | Any):
        new_class = super().__new__(mcs, name, bases, attrs)

        rewrote_map = type.__getattribute__(mcs, "_void_rewrote_map")
        rewrote_submap = rewrote_map.setdefault(new_class, {})

        special_rewrote_map = type.__getattribute__(mcs, "_void_special_rewrote_map")
        special_rewrote_submap = special_rewrote_map.setdefault(new_class, {})

        def new_proxy_method(name_):
            def proxy_method(cls_or_self, *args, **kwargs):
                method_map = {**special_rewrote_map.get(cls_or_self, {}), **special_rewrote_map.get(type(cls_or_self), {})}
                if name_ not in method_map:
                    raise TypeError
                return method_map[name_](cls_or_self, *args, **kwargs)

            return proxy_method

        def getattribute(cls_or_self, name_, *_, **__):
            method_map = {**rewrote_map.get(cls_or_self, {}), **rewrote_map.get(type(cls_or_self), {})}
            if name_ not in method_map:
                return cls_or_self
            def method(*args, **kwargs):
                return method_map[name_](cls_or_self, *args, **kwargs)
            return method

        none_method = type.__getattribute__(mcs, "_void_none_method")
        self_method = type.__getattribute__(mcs, "_void_self_method")
        custom_method = type.__getattribute__(mcs, "_void_custom_method")

        force_rewrite_methods = type.__getattribute__(mcs, "_void_force_rewrite_methods")
        mcs_protect_list = type.__getattribute__(mcs, "_void_mcs_protect_list")

        for rewrite_name, rewrite_m in {
            **auto_rewrite,
            **force_rewrite_methods,
            "__getattribute__": getattribute,
        }.items():
            if isinstance(rewrite_m, bool):
                act_m = self_method if rewrite_m else none_method
            elif callable(rewrite_m):
                act_m = rewrite_m
            else:
                act_m = custom_method(rewrite_m)

            rewrote_submap[rewrite_name] = act_m
            if rewrite_name.startswith("__") and rewrite_name.endswith("__"):
                special_rewrote_submap[rewrite_name] = act_m
                s_method = new_proxy_method(rewrite_name)
                type.__setattr__(new_class, rewrite_name, s_method)
                if rewrite_name not in mcs_protect_list:
                    type.__setattr__(mcs, rewrite_name, s_method)

        return new_class

    def __call__(cls, *_, **__):
        _void_instance_map = type.__getattribute__(cls, "_void_instance_map")
        if cls in _void_instance_map:
            return _void_instance_map[cls]

        _void_instance = super().__call__()
        _void_instance_map[cls] = _void_instance
        return _void_instance


class VoidClass(metaclass=VoidMeta):
    pass


__all__ = [
    "VoidClass",
    "VoidMeta",
]
