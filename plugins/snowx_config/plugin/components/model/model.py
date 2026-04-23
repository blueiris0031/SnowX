from pydantic import (
    BaseModel,
    TypeAdapter,
    ValidationError,

    field_validator,
)

from .meta import BaseConfigRootModelMeta, BaseConfigSubModelMeta
from ..config import get_model_config


class BaseConfigModel(BaseModel):
    model_config = get_model_config()

    @field_validator("*", mode="before")
    @classmethod
    def _cm_fallback_default(cls, value, info):
        field = cls.model_fields[info.field_name]
        try:
            TypeAdapter(field.annotation).validate_python(value)
            return value
        except ValidationError:
            return field.default if field.default_factory is None else field.default_factory()


class BaseConfigRootModel(BaseConfigModel, metaclass=BaseConfigRootModelMeta):
    pass


class BaseConfigSubModel(BaseConfigModel, metaclass=BaseConfigSubModelMeta, root_model=BaseConfigRootModel):
    pass


__all__ = [
    "BaseConfigRootModel",
    "BaseConfigSubModel",
]
