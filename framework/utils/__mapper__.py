from . import delayed_import
from . import lock
from . import module
from . import path
from . import queue
from . import serial_executor
from . import version
from . import worker
from ..constants.vmodule import VMODULE_ROOT_PATH, VMODULE_SUBROOT_PATH
from ..kernel.vmodule.expand import Adder


adder = Adder(f"{VMODULE_ROOT_PATH.ROOT}.{VMODULE_SUBROOT_PATH.UTILS}")


adder.get_sub_adder("delayed_import").auto_add(delayed_import)
adder.get_sub_adder("lock").auto_add(lock)
adder.get_sub_adder("module").auto_add(module)
adder.get_sub_adder("path").auto_add(path)
adder.get_sub_adder("queue").auto_add(queue)
adder.get_sub_adder("serial_executor").auto_add(serial_executor)
adder.get_sub_adder("version").auto_add(version)
adder.get_sub_adder("worker").auto_add(worker)
