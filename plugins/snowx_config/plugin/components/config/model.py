from typing import Any

from pydantic import ConfigDict


_default_config = {
    "extra": "allow",
    "validate_assignment": True,
    "validate_default": True,
    "hide_input_in_errors": True,
}


def get_model_config(**kwargs: Any) -> ConfigDict:
    return ConfigDict(**{**_default_config, **kwargs})


__all__ = ["get_model_config"]
