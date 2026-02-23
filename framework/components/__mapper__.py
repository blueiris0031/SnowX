from . import callback
from . import command_runner
from . import lock
from . import module_installer
from . import trigger
from ..constants.vmodule import VMODULE_ROOT_PATH, VMODULE_SUBROOT_PATH
from ..kernel.vmodule.expand import Adder


adder = Adder(f"{VMODULE_ROOT_PATH.ROOT}.{VMODULE_SUBROOT_PATH.COMPONENTS}")

adder.get_sub_adder("callback").auto_add(callback, recursive=True)
adder.get_sub_adder("command_runner").auto_add(command_runner)
adder.get_sub_adder("lock").auto_add(lock)
adder.get_sub_adder("module_installer").auto_add(module_installer)
adder.get_sub_adder("trigger").auto_add(trigger)
