from . import callback
from . import config
from . import event
from . import lock
from . import logger
from . import manager
from . import path
from . import plugin
from . import vmodule


from ..constants.vmodule import VMODULE_ROOT_PATH, VMODULE_SUBROOT_PATH
from ..kernel.vmodule.expand import Adder


api_adder = Adder(f"{VMODULE_ROOT_PATH.ROOT}.{VMODULE_SUBROOT_PATH.API}")

api_adder.get_sub_adder("config").auto_add(config)
api_adder.get_sub_adder("logger").auto_add(logger)

callback_api_adder = api_adder.get_sub_adder("callback")
callback_api_adder.auto_add(callback.registrar)

path_api_adder = api_adder.get_sub_adder("path")
path_api_adder.add_function("get_config_path")(path.get_config_path)
path_api_adder.add_function("get_data_path")(path.get_data_path)
path_api_adder.add_function("get_log_path")(path.get_log_path)
path_api_adder.add_function("get_temp_path")(path.get_temp_path)

plugin_api_adder = api_adder.get_sub_adder("plugin")
plugin_api_adder.auto_add(plugin.api)


kernel_adder = Adder(f"{VMODULE_ROOT_PATH.ROOT}.{VMODULE_SUBROOT_PATH.KERNEL}")

kernel_adder.get_sub_adder("event").auto_add(event)
kernel_adder.get_sub_adder("lock").auto_add(lock)
kernel_adder.get_sub_adder("manager").auto_add(manager)

callback_kernel_adder = kernel_adder.get_sub_adder("callback")
callback_kernel_adder.get_sub_adder("container").auto_add(callback.container)
callback_kernel_adder.get_sub_adder("executor").auto_add(callback.executor)
callback_kernel_adder.get_sub_adder("scheduler").auto_add(callback.scheduler)
callback_kernel_adder.get_sub_adder("wrapper").auto_add(callback.wrapper)

path_kernel_adder = kernel_adder.get_sub_adder("path")
path_kernel_adder.add_function(path.dir_plugin_path)

plugin_kernel_adder = kernel_adder.get_sub_adder("plugin")
plugin_kernel_adder.get_sub_adder("deps").auto_add(plugin.deps)
plugin_kernel_adder.get_sub_adder("importer").auto_add(plugin.importer)
plugin_kernel_adder.get_sub_adder("info").auto_add(plugin.info)
plugin_kernel_adder.get_sub_adder("manager").auto_add(plugin.manager)
plugin_kernel_adder.get_sub_adder("metadata").auto_add(plugin.metadata)

vmodule_kernel_adder = kernel_adder.get_sub_adder("vmodule")
vmodule_kernel_adder.get_sub_adder("manager").auto_add(vmodule.manager)
vmodule_kernel_adder.get_sub_adder("expand").auto_add(vmodule.expand)
