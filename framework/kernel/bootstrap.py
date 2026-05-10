from ..types.kernel.basic_kernel import BasicKernelProtocol


def _7c00(basic_kernel: BasicKernelProtocol) -> None:
    """
    Initialization pipeline.
    """
    from .kernel import Kernel
    kernel = Kernel()
    basic_kernel.submit_task(kernel.start, True)
    async def normal_stop_kernel() -> None: await kernel.stop()
    async def force_stop_kernel() -> None: await kernel.stop(True)
    basic_kernel.submit_stop_callback(normal_stop_kernel)
    basic_kernel.submit_panic_callback(force_stop_kernel)

    from .extensions.basic_kernel_interface import BasicKernelInterfaceExtension
    basic_kernel_interface_extension = BasicKernelInterfaceExtension(basic_kernel)
    async def load_basic_kernel_interface_extension() -> None: await kernel.load_extension(basic_kernel_interface_extension)
    basic_kernel.submit_task(load_basic_kernel_interface_extension, True)

    from .extensions.init import InitExtension
    init_extension = InitExtension()
    async def load_init_extension() -> None: await kernel.load_extension(init_extension)
    basic_kernel.submit_task(load_init_extension, True)


__all__ = [
    "_7c00",
]
