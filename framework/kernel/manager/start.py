from functools import partial

from .manager import framework_manager
from ..callback.scheduler import process_scheduler
from ..config import save_config
from ..event.distributor import event_distributor_manager
from ..plugin.manager import plugin_manager
from ...state.framework import SNOWX_STATE


framework_manager.inject_start_func(save_config)
framework_manager.inject_start_func(event_distributor_manager.start)
framework_manager.inject_start_func(partial(process_scheduler.start, SNOWX_STATE.ID))
framework_manager.inject_start_func(plugin_manager.load_all)

framework_manager.inject_stop_func(plugin_manager.unload_all)
framework_manager.inject_stop_func(partial(process_scheduler.stop, SNOWX_STATE.ID))
framework_manager.inject_stop_func(event_distributor_manager.stop)


__all__ = []
