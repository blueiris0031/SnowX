from collections import deque
from functools import partial
from typing import Callable, Coroutine, TypeVar, overload

from ...base.kernel import BaseKernelExtension
from ...constants.logger import ROOT_NAME
from ...mixins.loggable import LoggableMixin
from ...types.kernel import KernelProtocol
from ...utils.importtools import pre_injection_import
from ...utils.pathtools import get_src_path


_SUB_INIT_FUNC = Callable[[], Coroutine[None, None, None] | None]
_RF = TypeVar("_RF", bound=_SUB_INIT_FUNC)


class SubInitExtension(BaseKernelExtension, LoggableMixin):
    @property
    def identifier(self) -> str:
        return "sub_init"

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ("base_kernel_interface", )

    _register_map: dict[int, deque[_SUB_INIT_FUNC]] = {}

    @classmethod
    def _register_func(cls, func: _SUB_INIT_FUNC, level: int = 0) -> None:
        if level < 0:
            raise ValueError("'level' must be >= 0")
        if not callable(func):
            raise TypeError("'func' must be a callable")
        if level not in cls._register_map:
            cls._register_map[level] = deque()
        cls._register_map[level].append(func)

    @overload
    @classmethod
    def _registrar(cls, func: _RF, level: int = 0) -> _RF: ...
    @overload
    @classmethod
    def _registrar(cls, func: None = None, level: int = 0) -> Callable[[_RF], _RF]: ...
    @classmethod
    def _registrar(cls, func: _RF | None = None, level: int = 0) -> _RF | Callable[[_RF], _RF]:
        """
        Warning: Registering other functions within a registered function may result in undefined behavior.
        """
        def registrar(func_: _RF) -> _RF:
            cls._register_func(func_, level)
            return func_
        if func is None:
            return registrar
        return registrar(func)

    def __init__(self, default_level: int = 0) -> None:
        super().__init__()

        self._default_level = default_level
        self._kernel_pointer: KernelProtocol | None = None

        self.set_logger(f"{ROOT_NAME}.{self.identifier}")

    def _scanner(self) -> None:
        for sub_path in (src_path := get_src_path()).iterdir():
            if not sub_path.is_dir():
                continue
            if not (sub_path / "__sub_init__.py").is_file():
                continue

            package = f"{src_path.name}.{sub_path.name}"
            try:
                self.logger.info(f"Scanning '{package}' ...")
                pre_injection_import(
                    ".__sub_init__",
                    package,
                    kernel=self._kernel_pointer,
                    registrar=self._registrar,
                )
            except (ModuleNotFoundError, ImportError):
                continue
            except BaseException as exc:
                self.logger.critical(f"Scanning failed in '{package}' .", exc_info=exc)
                raise

    def _get_level_list(self) -> list[int]:
        register_level_list = list(self._register_map.keys())
        register_level_list.sort()
        return register_level_list

    def _submit_level(self, level: int = 0) -> None:
        if level not in self._register_map:
            return
        self.logger.info(f"Submit with level({level}) ...")
        func_queue = self._register_map[level]
        while func_queue:
            self._kernel_pointer.base_kernel_interface.submit_task(func_queue.popleft(), True)
        self.logger.info(f"Level({level}) submitted successfully.")
        self._register_map.pop(level, None)

    def _submit_with_max_level(self, level: int = 0) -> None:
        for l in self._get_level_list():
            if l > level:
                break
            self._submit_level(l)

    def _submit_all(self) -> None:
        for l in self._get_level_list():
            self._submit_level(l)

    def submit(self, level: int = -1) -> None:
        if level < 0:
            self._submit_all()
            return
        self._submit_with_max_level(level)

    def init(self, kernel: KernelProtocol) -> None:
        self._kernel_pointer = kernel
        self._kernel_pointer.base_kernel_interface.submit_task(self._scanner, True)
        self._kernel_pointer.base_kernel_interface.submit_task(partial(self.submit, self._default_level), True)

    def real_start(self) -> None:
        pass

    def real_stop(self, force: bool = False) -> None:
        pass


__all__ = [
    "SubInitExtension",
]
