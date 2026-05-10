from asyncio import Event

from ...constants.kernel_state import RunningStatus, StopType
from ...types.kernel_state import State
from ...utils.singleton import singleton


@singleton
class KernelState:
    def __init__(self) -> None:
        self._running_status_event_map = {status: Event() for status in RunningStatus}
        self._state = State(
            RunningStatus.Stopped,
            StopType.Normal,
            [],
        )

        self.set_running_status(RunningStatus.Stopped)

    def get_running_status(self) -> RunningStatus:
        return self._state.running_status

    def set_running_status(self, status: RunningStatus) -> None:
        self._state.running_status = status
        for k, event in self._running_status_event_map.items():
            if k is status:
                event.set()
            else:
                event.clear()

    async def wait_running_status(self, status: RunningStatus) -> None:
        await self._running_status_event_map[status].wait()

    def get_stop_type(self) -> StopType:
        return self._state.stop_type

    def set_stop_type(self, stop_type: StopType) -> None:
        self._state.stop_type = stop_type

    def get_ancillary_args(self) -> tuple[str, ...]:
        return tuple(self._state.ancillary_args)

    def clear_ancillary_args(self) -> None:
        self._state.ancillary_args.clear()

    def update_ancillary_args(self, args: tuple[str, ...]) -> None:
        self._state.ancillary_args.extend(args)


__all__ = [
    "KernelState",
]
