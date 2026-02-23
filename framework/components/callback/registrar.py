from inspect import getmodule

from .container import CallbackContainer
from ...base.callback import BaseCallbackExecutor, BaseCallbackWrapper
from ...kernel.logger import get_logger
from ...types.callback import (
    CallbackFunction,
    CallbackRegistrar,

    FunctionNameGetter,
    FunctionIdentifierGetter,
)
from ...types.plugin import Metadata


LOGGER = get_logger("CallbackRegistrar")


def _get_func_id(func: CallbackFunction) -> str:
    module = getmodule(func)
    if module is None:
        return ""
    metadata = getattr(module, "__plugin_metadata__", None)
    if not isinstance(metadata, Metadata):
        return ""
    return metadata.id


def _get_func_name(func: CallbackFunction) -> str:
    name = getattr(func, "__name__", None)
    if not isinstance(name, str):
        return "UnknownFunction"
    return name


def _getter(func: CallbackFunction, getter: FunctionIdentifierGetter | FunctionNameGetter, specified: str | None) -> str:
    if isinstance(specified, str) and specified:
        return specified
    if not callable(getter):
        return ""
    return getter(func)


def new_callback_registrar(
        container: CallbackContainer,
        callback_type: str,
        func_id_getter: FunctionIdentifierGetter | None = None,
        func_name_getter: FunctionNameGetter | None = None,
        wrapper: BaseCallbackWrapper | None = None,
        executor: BaseCallbackExecutor | None = None,
) -> CallbackRegistrar:
    """
    Create a new callback registrar.
    :param container: The callback container instance that needs to be registered.
    :param callback_type: The type of the callback.
    :param func_id_getter: This getter is used to obtain the unified identifier of the callback function.
     This identifier will be used for the storage and management of the callback container.
     If the identifier obtained by the getter is an empty string or none, this callback function will not be registered.
     If this parameter is none, use the built-in getter.
    :param func_name_getter: This getter is used to obtain the name of the callback function.
     Unlike the unified identifier getter, the name obtained by the name getter is only used for the logger.
     Even if the getter returns an empty string, it will register this callback function.
     If this parameter is none, use the built-in getter.
    :param wrapper: This wrapper will wrap the registered callback function. If this parameter is empty, the registered function will not be wrapped.
     For detailed information about the wrapper, please refer to [Components-Callback-Wrapper] chapter of the development document.
    :param executor: This executor will be passed into the wrapper. If the wrapper is none, this parameter will be ignored.
     For detailed information about the executor, please refer to [Components-Callback-Executor] chapter of the development document.
    :return: Callback registrar.
    """
    def registrar(identifier: str | CallbackFunction | None = None, func_name: str | None = None, **wrapper_kwargs) -> CallbackRegistrar | CallbackFunction:
        def decorator(func: CallbackFunction) -> CallbackFunction:
            id_ = _getter(func, func_id_getter or _get_func_id, identifier)
            name = _getter(func, func_name_getter or _get_func_name, func_name)

            if not id_:
                LOGGER.error(f"[UnknownIdentifier<{name}>]: Failed to register in <{callback_type}>, because the identifier is invalid.")
                return func

            if not callable(func):
                LOGGER.error(f"[{id_}<{name}>]: Failed to register in <{callback_type}>, because the incoming object is not callable.")
                return func

            if wrapper:
                try:
                    container.add(id_, name, callback_type, func, wrapper(func, executor, identifier=id_, func_name=name, **wrapper_kwargs))
                except Exception as e:
                    LOGGER.error(f"[{id_}<{name}>]: Failed to register in <{callback_type}>, because the callback function wrapping failed.", exc_info=e)
                    return func
            else:
                container.add(id_, name, callback_type, func, func)

            LOGGER.info(f"[{id_}<{name}>]: Successfully registered in <{callback_type}>.")
            return func

        if callable(identifier):
            be_decorated, identifier = identifier, None
            return decorator(be_decorated)

        return decorator

    return registrar


__all__ = [
    "new_callback_registrar",
]
