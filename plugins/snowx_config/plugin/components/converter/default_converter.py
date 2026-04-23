from typing import Callable

from pydantic import BaseModel

from .base_converter import BaseConverter


class DefaultConverter(BaseConverter, name="default"):
    def load(self, n_data: dict, call: Callable[..., BaseModel], **_) -> BaseModel:
        return call(**n_data)

    def dump(self, s_data: BaseModel, **_) -> dict:
        return s_data.model_dump()


__all__ = [
    "DefaultConverter",
]
