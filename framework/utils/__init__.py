from .importtools import delayed_import


__getattr__ = delayed_import(__package__)
