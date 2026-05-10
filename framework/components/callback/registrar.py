import logging
import traceback
import warnings
from typing import Callable, TypeVar

from .container import CallbackContainer
from ...types.callback import CallbackItem
from ...utils.void import VoidClass


_C = TypeVar("_C", bound=Callable)
_IR = Callable[[_C, ...], _C]
_R = Callable[[None, ...], _IR] | _IR


def _getter(
        func: Callable,
        getter: Callable[[Callable], str] | None,
        priority: str | None,
) -> str:
    if isinstance(priority, str) and priority:
        return priority
    try:
        return getter(func)
    except Exception:
        warnings.warn(f"An abnormality in the getter when obtaining the <{func}>, skip", RuntimeWarning)
        traceback.print_exc()
    return ""


def new_callback_registrar(
        container: CallbackContainer,
        callback_type: str,
        id_getter: Callable[[Callable], str] | None = None,
        name_getter: Callable[[Callable], str] | None = None,
        logger: logging.Logger | None = None,
) -> _R:
    """
    Create a new callback registrar.
    :param container: The callback container instance that needs to be registered.
    :param callback_type: The type of the callback.
    :param id_getter: This getter is used to obtain the unified identifier of the callback function.
     This identifier will be used for the storage and management of the callback container.
     If the identifier obtained by the getter is an empty string or none, this callback function will not be registered.
    :param name_getter: This getter is used to obtain the name of the callback function.
     Unlike the unified identifier getter, the name obtained by the name getter is only used for the logger.
     Even if the getter returns an empty string, it will register this callback function.
    :param logger: Logger.
    :return: Callback registrar.
    """
    c_logger = logger if logger else VoidClass()

    def registrar(
            func: _C | None = None,
            identifier: str | None = None,
            func_name: str | None = None,
            *extra_args,
            **extra_kwargs,
    ) -> _IR | _C:
        def decorator(func_: _C) -> _C:
            id_ = _getter(func_, id_getter, identifier)
            name = _getter(func_, name_getter, func_name)

            if not callable(func_):
                c_logger.error(f"[{id_}<{name}>]: Failed to register in <{callback_type}>, because the incoming object is not callable.")
                return func_

            if not id_:
                c_logger.error(f"[UnknownIdentifier<{name}>]: Failed to register in <{callback_type}>, because the identifier is invalid.")
                return func_

            container.auto_add(CallbackItem(callback_type, id_, name, func_, extra_args, extra_kwargs))
            c_logger.info(f"[{id_}<{name}>]: Successfully registered in <{callback_type}>.")
            return func_

        if func is not None:
            return decorator(func)

        return decorator

    c_logger.info(f"Successfully create the registrar: [{callback_type}]")
    return registrar


__all__ = [
    "new_callback_registrar",
]
