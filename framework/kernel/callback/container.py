from ...components.callback.container import CallbackContainer
from ...utils.singleton import ConfiguredSingletonMeta


GlobalCallbackContainer = ConfiguredSingletonMeta(
    "GlobalCallbackContainer",
    (CallbackContainer, ),
    {},
)


__all__ = [
    "GlobalCallbackContainer",
]
