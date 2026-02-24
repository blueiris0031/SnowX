from functools import partial

from .manager import framework_manager
from ..callback.scheduler import process_scheduler
from ..config import save_config
from ..event.distributor import event_distributor_manager
from ..plugin.manager import plugin_manager
from ...constants.framework import FRAMEWORK_METADATA


framework_manager.inject_start_func(save_config)
framework_manager.inject_start_func(event_distributor_manager.start)
framework_manager.inject_start_func(partial(process_scheduler.start, FRAMEWORK_METADATA.ID))
framework_manager.inject_start_func(plugin_manager.load_all)

framework_manager.inject_stop_func(event_distributor_manager.stop)
framework_manager.inject_stop_func(partial(process_scheduler.stop, FRAMEWORK_METADATA.ID))
framework_manager.inject_stop_func(plugin_manager.unload_all)


__all__ = []
