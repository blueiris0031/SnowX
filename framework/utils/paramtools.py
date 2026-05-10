from dataclasses import fields
from functools import wraps
from typing import Any, Callable, Literal, Mapping, ParamSpec, Sequence, TypeVar


def _get_args_generator(
        mode: Literal["ignore", "merge", "replace"],
        args: Sequence[Any],
) -> Callable[[Sequence[Any]], tuple[Any, ...]]:
    default_args = tuple(args)
    match mode:
        case "ignore":
            return lambda _: default_args
        case "merge":
            return lambda a: (*default_args, *a)
        case "replace":
            return lambda a: tuple(a) if a else default_args
        case _:
            raise ValueError(f"Unsupported mode: {mode}")


def _get_kwargs_generator(
        mode: Literal["ignore", "merge", "replace"],
        kwargs: Mapping[str, Any],
) -> Callable[[Mapping[str, Any]], dict[str, Any]]:
    default_kwargs = dict(kwargs)
    match mode:
        case "ignore":
            return lambda _: default_kwargs
        case "merge":
            return lambda k: {**default_kwargs, **k}
        case "replace":
            return lambda k: dict(k) if k else default_kwargs
        case _:
            raise ValueError(f"Unsupported mode: {mode}")


def get_params_generator(
        args_process_mode: Literal["ignore", "merge", "replace"],
        default_args: Sequence[Any],
        kwargs_process_mode: Literal["ignore", "merge", "replace"],
        default_kwargs: Mapping[str, Any],
) -> Callable[..., tuple[tuple[Any, ...], dict[str, Any]]]:
    args_gen = _get_args_generator(args_process_mode, default_args)
    kwargs_gen = _get_kwargs_generator(kwargs_process_mode, default_kwargs)
    return lambda *args, **kwargs: (args_gen(args), kwargs_gen(kwargs))


_P = ParamSpec("_P")
_R = TypeVar("_R")


def params_validator(validation_dataclass) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """
    Note: Dataclass fields and sequence shall strictly conform to the target function, \n
    and this decorator cannot be used with functions that have *args or **kwargs in their parameter signatures.
    """
    field_namelist = [field.name for field in fields(validation_dataclass)]
    field_num = len(field_namelist)

    def wrapper(func: Callable[_P, _R]) -> Callable[_P, _R]:
        def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            data_cls = validation_dataclass(*args, **kwargs)
            arg_length = len(args)
            validated_args = [getattr(data_cls, field_namelist[index]) for index in range(0, arg_length)]
            validated_kwargs = {(fn := field_namelist[index]): getattr(data_cls, fn) for index in range(arg_length, field_num)}
            return func(*validated_args, **validated_kwargs)
        return wraps(func)(wrapped)
    return wrapper


__all__ = [
    "get_params_generator",
    "params_validator",
]
