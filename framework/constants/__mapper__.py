from . import callback
from . import command_runner
from . import framework
from . import path
from . import vmodule
from ..constants.vmodule import VMODULE_ROOT_PATH, VMODULE_SUBROOT_PATH
from ..kernel.vmodule.expand import Adder


adder = Adder(f"{VMODULE_ROOT_PATH.ROOT}.{VMODULE_SUBROOT_PATH.CONSTANTS}")

adder.get_sub_adder("callback").auto_add(callback)
adder.get_sub_adder("command_runner").auto_add(command_runner)
adder.get_sub_adder("framework").auto_add(framework)
adder.get_sub_adder("path").auto_add(path)
adder.get_sub_adder("vmodule").auto_add(vmodule)
