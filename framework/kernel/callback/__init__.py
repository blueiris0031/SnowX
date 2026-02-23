from ...utils.delayed_import import delayed_import


__all__ = [
    "container",
    "executor",
    "registrar",
    "scheduler",
    "wrapper",
]


__getattr__ = delayed_import(__all__, __package__)
