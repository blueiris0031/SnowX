import asyncio
from pathlib import Path

from ..constants.command_runner import ProcessStatus
from ..kernel.logger import get_logger


LOGGER = get_logger("CommandRunner")


class AsyncCommandRunner:
    def __init__(self, program: str | Path, *args: str):
        self._program = Path(program)
        self._args = args

        self._status = ProcessStatus.not_running
        self._process: asyncio.subprocess.Process | None = None

    async def start(self) -> bool:
        if self._status != ProcessStatus.not_running:
            LOGGER.warning(f"The process status is not <{ProcessStatus.not_running}>: <{self._program}>")
            return True

        try:
            self._process = await asyncio.create_subprocess_exec(
                self._program,
                *self._args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self._status = ProcessStatus.running
            return True
        except asyncio.CancelledError:
            raise asyncio.CancelledError
        except FileNotFoundError:
            LOGGER.error(f"File not found: <{self._program}>")
        except PermissionError:
            LOGGER.error(f"Permission denied: <{self._program}>")
        except Exception as e:
            LOGGER.error(f"Unexpected error: <{self._program}>", exc_info=e)

        return False

    async def stop(self, terminate_timeout: int) -> None:
        if self._status != ProcessStatus.running:
            LOGGER.warning(f"The process status is not <{ProcessStatus.running}>: <{self._program}>")
            return

        self._process.terminate()
        try:
            await asyncio.wait_for(self._process.wait(), timeout=terminate_timeout)
            self._status = ProcessStatus.run_failed
            return

        except asyncio.TimeoutError:
            LOGGER.warning(f"Terminated timeout: <{self._program}>")

        self._process.kill()
        await self._process.wait()
        self._status = ProcessStatus.run_failed

    async def wait(self, timeout: int = 0) -> bool:
        if self._status != ProcessStatus.running:
            LOGGER.warning(f"The process status is not <{ProcessStatus.running}>: <{self._program}>")
            return True

        timeout = max(timeout, 0)

        try:
            if timeout == 0:
                await self._process.wait()
            else:
                await asyncio.wait_for(self._process.wait(), timeout=timeout)

            if self._process.returncode == 0:
                self._status = ProcessStatus.run_success
            else:
                self._status = ProcessStatus.run_failed

            return True

        except asyncio.TimeoutError:
            LOGGER.error(f"Timeout: <{self._program}>")

        return False

    async def get_result(self, encoding: str = "utf-8") -> tuple[int | None, str, str]:
        if self._status == ProcessStatus.not_running or self._status == ProcessStatus.running:
            return None, "", ""

        stdout, stderr = await self._process.communicate()
        return self._process.returncode, stdout.decode(encoding=encoding), stderr.decode(encoding=encoding)


__all__ = [
    "AsyncCommandRunner",
]
