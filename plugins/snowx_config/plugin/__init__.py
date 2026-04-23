from typing import Any

from .components import (
    config,
    converter,
    model,
    reader,
    clock,
)
from .constants.model import MODEL_TYPE
from snowx.api.path import get_config_path
from snowx.api.callback import on_init, on_exit


BaseConfigRootModel = model.BaseConfigRootModel
BaseConfigSubModel = model.BaseConfigSubModel


def gen_root_model_kwargs(
        name: str,
        f_type: str = "json",
        f_converter: str = "default",
) -> dict[str, Any]:
    f_reader = reader.BaseReader.get_reader(f_type)
    if f_reader:
        f_reader = f_reader()
        f_path = get_config_path(f"{name}.{f_reader.file_suffix}")
    else:
        f_path = None

    converter_ = converter.BaseConverter.get_converter(f_converter)

    return {
        "config_path": f_path,
        "config_reader": f_reader,
        "config_converter": converter_() or None,
    }


clock_worker = clock.clock_worker


@on_init
async def c_init():
    await clock_worker.start()


@on_exit
async def c_exit():
    await clock_worker.stop()


__all__ = [
    "config",
    "converter",
    "model",
    "reader",
    "MODEL_TYPE",

    "BaseConfigRootModel",
    "BaseConfigSubModel",
    "gen_root_model_kwargs",
]
