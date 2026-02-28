from snowx.api.callback import on_exit
from snowx.plugins.lazy_init import on_lazy_init
from tortoise import Tortoise


@on_lazy_init
async def tortoise_init() -> None:
    await Tortoise.init()


@on_exit
async def tortoise_exit() -> None:
    await Tortoise.close_connections()
