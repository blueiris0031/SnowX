from . import version
from ..constants.vmodule import VMODULE_ROOT_PATH, VMODULE_SUBROOT_PATH
from ..kernel.vmodule.expand import Adder


adder = Adder(f"{VMODULE_ROOT_PATH.ROOT}.{VMODULE_SUBROOT_PATH.ERROR}")

adder.get_sub_adder("version").auto_add(version)
