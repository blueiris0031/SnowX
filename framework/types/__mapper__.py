from . import callback
from . import event
from . import plugin
from ..constants.vmodule import VMODULE_ROOT_PATH, VMODULE_SUBROOT_PATH
from ..kernel.vmodule.expand import Adder


adder = Adder(f"{VMODULE_ROOT_PATH.ROOT}.{VMODULE_SUBROOT_PATH.TYPES}")


adder.get_sub_adder("callback").auto_add(callback)
adder.get_sub_adder("event").auto_add(event)
adder.get_sub_adder("plugin").auto_add(plugin)
