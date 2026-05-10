from dataclasses import dataclass, field, fields
from typing import Any, Callable, Type, TypeVar, overload
from uuid import uuid4


_VALIDATION_ID: str
if "_VALIDATION_ID" not in globals(): # Compatible with 'reload_module'.
    _VALIDATION_ID = uuid4().hex


_DC = TypeVar("_D_CLS", bound=Type)


def validation_field(validator: Callable[[Any], Any], /, **field_kwargs):
    """
    This field will carry data validation information in the metadata. The data validation function must return a valid data type. \n
    """
    metadata = field_kwargs.pop("metadata", {})
    if _VALIDATION_ID in metadata:
        raise RuntimeError("Unsupported field metadata, VALIDATION_ID conflict")
    if not callable(validator):
        raise TypeError("'validator' must be callable")
    return field(metadata={_VALIDATION_ID: validator, **metadata}, **field_kwargs)


_EMPTY_VALIDATOR = lambda x: x
def _validator(self) -> None:
    for f in fields(self):
        validator = f.metadata.get(_VALIDATION_ID, _EMPTY_VALIDATOR)
        value = getattr(self, f.name)
        object.__setattr__(self, f.name, validator(value))


@overload
def validation_dataclass(cls: _DC, /, **dataclass_kwargs) -> _DC: ...
@overload
def validation_dataclass(cls: None = None, /, **dataclass_kwargs) -> Callable[[_DC], _DC]: ...
def validation_dataclass(cls: _DC | None = None, /, **dataclass_kwargs) -> _DC | Callable[[_DC], _DC]:
    """
    To implement validation functionality, 'validation_field' must be used in conjunction. \n
    After using this decorator, there is no need to apply the 'dataclass' decorator separately. 'dataclass_kwargs' will be passed through directly to the internal dataclass.
    """
    def init_dataclass(cls_: _DC) -> _DC:
        origin_post_init = getattr(cls_, "__post_init__", lambda _: None)
        def merged_post_init(self) -> None:
            origin_post_init(self)
            _validator(self)
        cls_.__post_init__ = merged_post_init
        return dataclass(**dataclass_kwargs)(cls_)

    if cls is None:
        return init_dataclass
    return init_dataclass(cls)


_V = TypeVar("_VT")


def new_type_validator(type_: Type[_V], default: _V | None = None) -> Callable[[_V | None], _V]:
    """
    Logic: If the value is None, replace it with the default value. Raise a TypeError if the type does not match. \n
    Note: The default value will also be validated. If you do not want to set a default value, simply set default to None.
    """
    def validator(value: _V | None) -> _V:
        value = default if value is None else value
        if not isinstance(value, type_):
            raise TypeError(f"Expected {type_.__name__}, but got {type(value).__name__}")
        return value
    return validator


__all__ = [
    "validation_field",
    "validation_dataclass",
    "new_type_validator",
]
