from dataclasses import dataclass

from ..constants.kernel_state import RunningStatus, StopType


@dataclass
class State:
    running_status: RunningStatus
    stop_type: StopType
    ancillary_args: list[str]


__all__ = [
    "State",
]
