from . import framework

from ..constants.vmodule import VMODULE_ROOT_PATH, VMODULE_SUBROOT_PATH
from ..kernel.vmodule.expand import Adder


api_adder = Adder(f"{VMODULE_ROOT_PATH.ROOT}.{VMODULE_SUBROOT_PATH.API}.state")

api_adder.add_function()(framework.wait_started)
api_adder.add_function()(framework.wait_stopping)


kernel_adder = Adder(f"{VMODULE_ROOT_PATH.ROOT}.{VMODULE_SUBROOT_PATH.KERNEL}.state")

kernel_adder.add_function()(framework.set_started)
kernel_adder.add_function()(framework.set_stopping)


state_adder = Adder(f"{VMODULE_ROOT_PATH.ROOT}.{VMODULE_SUBROOT_PATH.STATE}")

state_adder.add_object("SNOWX_STATE", framework.SNOWX_STATE)
state_adder.add_object("SNOWX_STOP_STATE", framework.SNOWX_STOP_STATE)
