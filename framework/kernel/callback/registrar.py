from .container import global_callback_container
from .executor import executor
from .wrapper import empty_wrapper, process_wrapper, autorun_wrapper
from ...components.callback.registrar import new_callback_registrar
from ...constants.callback import CALLBACK_TYPE


on_init = new_callback_registrar(
    global_callback_container,
    CALLBACK_TYPE.INIT,
    wrapper=empty_wrapper,
    executor=executor,
)

on_exit = new_callback_registrar(
    global_callback_container,
    CALLBACK_TYPE.EXIT,
    wrapper=empty_wrapper,
    executor=executor,
)

on_process = new_callback_registrar(
    global_callback_container,
    CALLBACK_TYPE.PROCESS,
    wrapper=process_wrapper,
    executor=executor,
)

on_autorun = new_callback_registrar(
    global_callback_container,
    CALLBACK_TYPE.AUTORUN,
    wrapper=autorun_wrapper,
    executor=executor,
)


__all__ = [
    "on_init",
    "on_exit",
    "on_process",
    "on_autorun",
]
