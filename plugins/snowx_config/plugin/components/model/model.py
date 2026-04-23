from pydantic import BaseModel

from .meta import BaseConfigRootModelMeta, BaseConfigSubModelMeta
from ..config import get_model_config


class BaseConfigRootModel(BaseModel, metaclass=BaseConfigRootModelMeta):
    model_config = get_model_config()


class BaseConfigSubModel(BaseModel, metaclass=BaseConfigSubModelMeta, root_model=BaseConfigRootModel):
    model_config = get_model_config()


__all__ = [
    "BaseConfigRootModel",
    "BaseConfigSubModel",
]
