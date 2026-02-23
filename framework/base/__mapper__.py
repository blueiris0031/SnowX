from . import callback
from . import trigger
from ..constants.vmodule import VMODULE_ROOT_PATH, VMODULE_SUBROOT_PATH
from ..kernel.vmodule.expand import Adder


adder = Adder(f"{VMODULE_ROOT_PATH.ROOT}.{VMODULE_SUBROOT_PATH.BASE}")

adder.get_sub_adder("callback").auto_add(callback)
adder.get_sub_adder("trigger").auto_add(trigger)
