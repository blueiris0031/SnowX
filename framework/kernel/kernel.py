import asyncio
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, Self

from ..base.lifecycle import BaseLifeCycle, with_running_check
from ..constants.logger import ROOT_NAME
from ..mixins.executor import ExecutorMixin
from ..mixins.loggable import LoggableMixin
from ..types.kernel.kernel import KernelProtocol, KernelExtensionProtocol
from ..types.loop import with_loop_check
from ..utils.deps import gen_priority_list, gen_priority_list_by_reverse_dependency
from ..utils.singleton import singleton_decorator


@singleton_decorator
class Kernel(BaseLifeCycle, ExecutorMixin, LoggableMixin, KernelProtocol):
    def __init__(self):
        super().__init__()

        self._load_lock = asyncio.Lock()
        self._loaded_extensions: dict[str, KernelExtensionProtocol] = {}
        self._loaded_extensions_proxy = MappingProxyType(self._loaded_extensions)

        self.set_logger(f"{ROOT_NAME}.kernel")

    @property
    def loaded_extensions(self) -> MappingProxyType[str, KernelExtensionProtocol]:
        return self._loaded_extensions_proxy

    def __getattr__(self, extension_id: str) -> KernelExtensionProtocol:
        if extension_id not in self._loaded_extensions:
            raise AttributeError(f"Cannot find extension '{extension_id}'")
        return self._loaded_extensions[extension_id]

    async def _run_method(
            self,
            extension: KernelExtensionProtocol,
            method_name: str,
            log_type: str,
            raise_exc: bool = True,
            args: Iterable | None = None,
            kwargs: Mapping[str, Any] | None = None,
    ) -> None:
        method: Callable = getattr(extension, method_name)
        is_success, exc = await self.executor(method)(*args or (), **kwargs or {})
        if is_success:
            self.logger.info(f"Extension '{extension.identifier}' {method_name} {log_type} executing success.")
            return

        self.logger.error(f"Extension '{extension.identifier}' {method_name} {log_type} executing failed.", exc_info=exc)
        if raise_exc:
            raise exc

    async def _run_init_hook(self, extension: KernelExtensionProtocol) -> None:
        await self._run_method(extension, "init", "hook", args=[self])

    async def _run_start_method(self, extension: KernelExtensionProtocol) -> None:
        await self._run_method(extension, "start", "method")

    async def _run_stop_method(self, extension: KernelExtensionProtocol, force: bool = False) -> None:
        await self._run_method(extension, "stop", "method", False, args=[force])

    async def _run_exit_hook(self, extension: KernelExtensionProtocol) -> None:
        await self._run_method(extension, "exit", "hook", False, args=[self])

    async def _load_single_extension(self, extension: KernelExtensionProtocol) -> None:
        id_ = extension.identifier
        self.logger.info(f"Trying to load extension '{id_}' ...")

        try:
            await self._run_init_hook(extension)
            await self._run_start_method(extension)
        except Exception as exc:
            self.logger.error(f"Cannot load extension '{id_}'.")
            await self._run_exit_hook(extension)
            raise exc

    @with_loop_check
    @with_running_check(True)
    async def load_extension(self: Self, extension: KernelExtensionProtocol) -> None:
        async with self._load_lock:
            if not self.running:
                raise RuntimeError("Kernel is not running")
            if not isinstance(extension, KernelExtensionProtocol):
                raise TypeError(f"Extension '{extension}' is not a KernelExtensionProtocol")

            id_ = extension.identifier
            self.logger.info(f"Checking extension '{id_}' ...")
            if id_ in self._loaded_extensions:
                self.logger.info(f"Extension '{id_}' already loaded.")
                return

            if missing_set := {dep for dep in extension.dependencies if dep not in self._loaded_extensions}:
                missing_msg = "', '".join(missing_set)
                self.logger.error(msg := f"Cannot load extension '{id_}', because dependencies are missing: '{missing_msg}'")
                raise RuntimeError(msg)

            await self._load_single_extension(extension)
            self._loaded_extensions[id_] = extension
            self.logger.info(f"Extension '{id_}' loaded successfully.")

    async def _unload_single_extension(self, extension: KernelExtensionProtocol, force: bool = False) -> None:
        id_ = extension.identifier
        self.logger.info(f"Trying to unload extension '{id_}' ...")
        await self._run_stop_method(extension, force)
        await self._run_exit_hook(extension)

    def _gen_dependency_table(self) -> dict[str, tuple[str, ...]]:
        return {k: v.dependencies for k, v in self._loaded_extensions.items()}

    async def _builtin_unload_extension(self, extension_id: str | None = None, force: bool = False) -> None:
        if extension_id is None:
            priority_list, _ = gen_priority_list(self._gen_dependency_table())
        else:
            self.logger.info(f"Checking extension '{extension_id}' ...")
            if extension_id not in self._loaded_extensions:
                self.logger.info(f"Extension '{extension_id}' not loaded.")
                return
            priority_list, _ = gen_priority_list_by_reverse_dependency(self._gen_dependency_table(), extension_id)

        for unload_id in reversed(priority_list):
            self.logger.info(f"Need to unload extension '{unload_id}' ...")
            await self._unload_single_extension(self._loaded_extensions.pop(unload_id), force)
            self.logger.info(f"Extension '{unload_id}' unloaded successfully.")

    @with_loop_check
    @with_running_check(True)
    async def unload_extension(self: Self, extension_id: str | None = None, force: bool = False) -> None:
        """
        If extension_id is None, unload all extensions.
        """
        async with self._load_lock:
            if not self.running:
                raise RuntimeError("Kernel is not running")
            await self._builtin_unload_extension(extension_id, force)

    async def real_start(self) -> None:
        self.logger.info(f"Kernel started successfully.")

    async def real_stop(self, force: bool = False) -> None:
        self.logger.info(f"Stopping kernel...")
        await self._builtin_unload_extension(force=force)
        self.logger.info(f"Kernel stopped successfully.")


__all__ = [
    "Kernel",
]
