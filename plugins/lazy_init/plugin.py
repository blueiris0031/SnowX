from snowx.api.callback import on_autorun
from snowx.api.state import wait_started
from snowx.components.callback.container import CallbackContainer
from snowx.components.callback.executor import BuiltinExecutor
from snowx.components.callback.registrar import new_callback_registrar
from snowx.components.callback.scheduler import SchedulerManager, SingleExecutionSchedulerItem
from snowx.components.callback.wrapper import EmptyWrapper
from snowx.constants.callback import EXECUTION_METHOD
from snowx.plugins.more_trigger import ResetTrigger
from snowx.utils.serial_executor import serial_executor


CB_TYPE = "lazy_init"


container = CallbackContainer()
on_lazy_init = new_callback_registrar(
    container,
    CB_TYPE,
    wrapper = EmptyWrapper(),
    executor = BuiltinExecutor(),
)
scheduler = SchedulerManager(
    CB_TYPE,
    container,
    SingleExecutionSchedulerItem,
    {"execution_method": EXECUTION_METHOD.SERIAL},
)


trigger = ResetTrigger()
trigger.enable()

@on_autorun(trigger=trigger)
async def lazy_init():
    await wait_started()

    plugin_id = container.get_plugin_id(CB_TYPE)
    if not plugin_id:
        return

    for id_ in plugin_id:
        await scheduler.start(id_)
        await scheduler.stop(id_)

        container.remove_from_plugin_id(id_)


__all__ = [
    "on_lazy_init",
]
