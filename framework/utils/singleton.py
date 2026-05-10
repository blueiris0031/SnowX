from typing import Any, Iterable, Type


class SingletonMeta(type):
    _instance_map: dict[Type[Any], Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls in cls._instance_map:
            return cls._instance_map[cls]

        new_instance = super().__call__(*args, **kwargs)
        cls._instance_map[cls] = new_instance
        return new_instance


class SingletonClass(metaclass=SingletonMeta):
    pass


class ConfiguredSingletonMeta(SingletonMeta):
    _params_map: dict[Type, tuple[bool, Iterable[Any], dict[str, Any]]] = {}

    def __new__(
            mcs,
            name: str,
            bases: tuple[Type],
            attrs: dict[str, Any],
            allow_cover_params: bool = False,
            instance_init_args: Iterable[Any] | None = None,
            instance_init_kwargs: dict[str, Any] | None = None,
            **kwargs: Any,
    ):
        new_class = super().__new__(mcs, name, bases, attrs, **kwargs)
        mcs._params_map[new_class] = (allow_cover_params, instance_init_args or (), instance_init_kwargs or {})
        return new_class

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        allow_cover, d_args, d_kwargs = cls._params_map.get(cls)

        c_args = [*d_args]
        c_kwargs = {**d_kwargs}
        if allow_cover:
            c_args.extend(args)
            c_kwargs.update(kwargs)

        return super().__call__(*c_args, **c_kwargs)


class ConfiguredSingletonClass(metaclass=ConfiguredSingletonMeta):
    pass


__all__ = [
    "SingletonMeta",
    "SingletonClass",
    "ConfiguredSingletonMeta",
    "ConfiguredSingletonClass",
]
