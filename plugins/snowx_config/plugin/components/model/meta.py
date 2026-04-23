from pathlib import Path
from typing import Any, Type

from pydantic import (
    BaseModel,
    TypeAdapter,
    ValidationError,

    field_validator,
)

from ..converter import BaseConverter
from ..reader import BaseReader
from ...constants.model import MODEL_TYPE


class BaseConfigModelMeta(type(BaseModel)):
    @classmethod
    def add_cm_get_model_type(mcs, model_class: Any) -> None:
        @classmethod
        def _cm_get_model_type(cls) -> str:
            return cls._cm_model_type
        model_class._cm_get_model_type = _cm_get_model_type

    @classmethod
    def add_cm_fallback_default(mcs, model_class: Any) -> None:
        @field_validator("*", mode="before")
        @classmethod
        def _cm_fallback_default(cls, value, info):
            field = cls.model_fields[info.field_name]
            try:
                TypeAdapter(field.annotation).validate_python(value)
                return value
            except ValidationError:
                return field.default if field.default_factory is None else field.default_factory()

        model_class._cm_fallback_default = _cm_fallback_default

    def __new__(
            mcs,
            name: str,
            bases: tuple[Type],
            attrs: dict[str, Any],
            model_type: str = MODEL_TYPE.NULL,
            **kwargs: Any,
    ):
        model_class = super().__new__(mcs, name, bases, attrs, **kwargs)

        for field_name, field_info in model_class.model_fields.items():
            if field_info.is_required():
                raise TypeError(f"Model '{name}' has required field '{field_name}'")

        model_class._cm_model_type = model_type
        mcs.add_cm_get_model_type(model_class)
        return model_class

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class BaseConfigRootModelMeta(BaseConfigModelMeta):
    _config_map = {}

    @classmethod
    def add_cm_is_persistent_conf(mcs, model_class: Any) -> None:
        @classmethod
        def _cm_is_persistent_conf(cls) -> bool:
            return bool(
                cls._cm_config_path
                and cls._cm_config_reader
                and cls._cm_config_converter
            )

        model_class._cm_is_persistent_conf = _cm_is_persistent_conf

    @classmethod
    def add_cm_save_config(mcs, model_class: Any) -> None:
        def _cm_save_config(
                self,
                reader_kwargs: dict[str, Any] | None = None,
                converter_kwargs: dict[str, Any] | None = None,
        ) -> None:
            if not self._cm_is_persistent_conf():
                return

            n_config = self._cm_config_converter.safe_dump(self, **(converter_kwargs or {}))
            self._cm_config_reader.safe_write(self._cm_config_path, n_config, **(reader_kwargs or {}))

        model_class._cm_save_config = _cm_save_config

    @classmethod
    def has_instance(mcs, config_path: Path, model_class: Any) -> bool:
        if config_path not in mcs._config_map:
            return False

        recorded_class = mcs._config_map[config_path][0]
        return recorded_class is model_class

    @classmethod
    def add_cm_has_instance(mcs, model_class: Any) -> None:
        @classmethod
        def _cm_has_instance(cls) -> bool:
            return mcs.has_instance(cls._cm_config_path, cls)

        model_class._cm_has_instance = _cm_has_instance

    @classmethod
    def rewrite_setattr(mcs, model_class: Any) -> None:
        origin_setattr = model_class.__setattr__

        def __setattr__(self, name: str, value: Any) -> None:
            origin_setattr(self, name, value)
            if not self._cm_has_instance():
                return
            self._cm_save_config()

        model_class.__setattr__ = __setattr__

    def __new__(
            mcs,
            name: str,
            bases: tuple[Type],
            attrs: dict[str, Any],
            config_path: Path | None = None,
            config_reader: BaseReader | None = None,
            config_converter: BaseConverter | None = None,
            **kwargs: Any,
    ):
        model_class = super().__new__(mcs, name, bases, attrs, model_type=MODEL_TYPE.ROOT, **kwargs)

        model_class._cm_config_path = config_path
        model_class._cm_config_reader = config_reader
        model_class._cm_config_converter = config_converter

        mcs.add_cm_is_persistent_conf(model_class)
        mcs.add_cm_save_config(model_class)
        mcs.add_cm_has_instance(model_class)
        mcs.rewrite_setattr(model_class)

        return model_class

    def __call__(
            cls,
            reader_kwargs: dict[str, Any] | None = None,
            converter_kwargs: dict[str, Any] | None = None,
    ):
        call = super().__call__

        if not cls._cm_is_persistent_conf():
            return call()

        if not cls.has_instance(cls._cm_config_path, cls):
            raw_config = cls._cm_config_reader.safe_read(cls._cm_config_path, **(reader_kwargs or {}))
            instance = cls._cm_config_converter.safe_load(raw_config, call, **(converter_kwargs or {})) or call()
            cls._config_map[cls._cm_config_path] = (cls, instance)

        return cls._config_map[cls._cm_config_path][1]


class BaseConfigSubModelMeta(BaseConfigModelMeta):
    @classmethod
    def add_cm_save_config(mcs, model_class: Any) -> None:
        def _cm_save_config(
                self,
                reader_kwargs: dict[str, Any] | None = None,
                converter_kwargs: dict[str, Any] | None = None,
        ) -> None:
            self._cm_root_model()._cm_save_config(reader_kwargs, converter_kwargs)

        model_class._cm_save_config = _cm_save_config

    @classmethod
    def add_cm_has_instance(mcs, model_class: Any) -> None:
        @classmethod
        def _cm_has_instance(cls) -> bool:
            return cls._cm_root_model._cm_has_instance()

        model_class._cm_has_instance = _cm_has_instance

    @classmethod
    def rewrite_setattr(mcs, model_class: Any) -> None:
        origin_setattr = model_class.__setattr__

        def __setattr__(self, name: str, value: Any) -> None:
            origin_setattr(self, name, value)
            if not self._cm_has_instance():
                return
            self._cm_save_config()

        model_class.__setattr__ = __setattr__

    def __new__(
            mcs,
            name: str,
            bases: tuple[Type],
            attrs: dict[str, Any],
            root_model: Any = None,
            **kwargs: Any,
    ):
        if type(root_model) is not BaseConfigRootModelMeta:
            raise TypeError(f"Invalid root model")

        model_class = super().__new__(mcs, name, bases, attrs, model_type=MODEL_TYPE.SUB, **kwargs)

        model_class._cm_root_model = root_model

        mcs.add_cm_save_config(model_class)
        mcs.add_cm_has_instance(model_class)
        mcs.rewrite_setattr(model_class)

        return model_class


__all__ = [
    "BaseConfigModelMeta",
    "BaseConfigRootModelMeta",
    "BaseConfigSubModelMeta",
]
