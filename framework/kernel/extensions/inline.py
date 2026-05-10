from importlib.metadata import distributions
from site import addsitedir

from ...base.kernel import BaseKernelExtension
from ...constants.inline import INLINE_DIRECTORY_NAME
from ...utils.pathtools import is_valid_name, get_main_path


class InlineExtension(BaseKernelExtension):
    @property
    def identifier(self) -> str:
        return "inline"

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ()

    _loaded_inline: set[str] = set()

    @classmethod
    def _load_inline(cls):
        base_path = get_main_path().parent / INLINE_DIRECTORY_NAME
        installed_list = {x.metadata["Name"].lower() for x in distributions()}
        for inline_path in base_path.iterdir():
            if (pack_name := inline_path.name.lower()) in cls._loaded_inline:
                continue
            if pack_name in installed_list:
                continue
            if not is_valid_name(pack_name):
                continue
            if not inline_path.is_dir():
                continue
            addsitedir(str(inline_path))
            cls._loaded_inline.add(pack_name)

    def __init__(self) -> None:
        super().__init__()

    @property
    def loaded_inline(self) -> tuple[str, ...]:
        return tuple(self._loaded_inline)

    def real_start(self) -> None:
        self._load_inline()

    def real_stop(self, force: bool = False) -> None:
        pass


__all__ = [
    "InlineExtension",
]
