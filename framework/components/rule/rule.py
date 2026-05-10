from ...types.rule import RuleProtocol


class FixedValueRule(RuleProtocol):
    """
    Rule that returns a fixed value.
    """
    def __init__(self, return_value: int) -> None:
        self._return_value = return_value

    def __call__(self, count: int) -> int:
        return self._return_value

    def reset(self) -> None:
        pass


class CountingThresholdRule(RuleProtocol):
    def __init__(
            self,
            *threshold_group: tuple[int, int],
            default: int = 0,
    ) -> None:
        self._t_group_map = dict(threshold_group)
        self._t_group_index = tuple(sorted(self._t_group_map.keys(), reverse=True))
        self._default = default

    def __call__(self, count: int) -> int:
        for i in self._t_group_index:
            if count >= i:
                return self._t_group_map[i]
        return self._default

    def reset(self) -> None:
        pass


__all__ = [
    "FixedValueRule",
    "CountingThresholdRule",
]
