from typing import Any, Callable, TypeVar
from weakref import WeakValueDictionary

from ...types.rule import RuleProtocol
from ...utils.dataclass import new_type_validator, validation_dataclass, validation_field


_N = TypeVar("_N", bound=int)
_R = TypeVar("_R", bound=RuleProtocol)
_RULE_CALLBACK = Callable[[int], int]


_const_callback_map: WeakValueDictionary[int, _RULE_CALLBACK] = WeakValueDictionary()


def _get_const_callback(n: _N) -> Callable[[int], _N]:
    if n in _const_callback_map:
        return _const_callback_map[n]
    return _const_callback_map.setdefault(n, lambda _: n)


def _callback_validator(callback: _RULE_CALLBACK | int) -> _RULE_CALLBACK:
    if isinstance(callback, int):
        callback = _get_const_callback(callback)
    if not callable(callback):
        raise TypeError("'callback' must be callable")
    return callback


@validation_dataclass(frozen=True)
class _RuleItem: # For 'RuleEngine'.
    rule: RuleProtocol = validation_field(new_type_validator(RuleProtocol))
    callback: _RULE_CALLBACK = validation_field(_callback_validator, default=0)


class RuleEngine:
    """
    RuleEngine
    Example:
        engine = RuleEngine(
            rule1 = YourRule1(),
            rule2 = (YourRule2(), ),
            rule3 = (YourRule3(), 1), # Here's 1 will add to the count when this rule is called
            rule4 = (YourRule4(), callback), # Here's callback will run and get the return value, which will be added to the count
        )

        rule1_result = engine.rule1
        rule2_result = engine.rule2
        rule3_result = engine.rule3
        rule4_result = engine.rule4

        engine.reset() # The reset count is 0 and reset all the rule.
    Note: The callback function will be passed the engine's current count upon execution.
    """

    @staticmethod
    def _rule_formatter(rule: RuleProtocol | tuple[RuleProtocol] | tuple[RuleProtocol, int | _RULE_CALLBACK]) -> _RuleItem:
        if isinstance(rule, tuple):
            return _RuleItem(*rule)
        return _RuleItem(rule)

    def __init__(self, **rule: RuleProtocol | tuple[RuleProtocol] | tuple[RuleProtocol, int | _RULE_CALLBACK]):
        """
        Note: If an exception is raised during callback execution, it may result in an uncontrollable engine state.
        """
        self._rule_map: dict[str, _RuleItem] = {name: self._rule_formatter(r) for name, r in rule.items()}
        self._count = 0

    def _add_count(self, a: int) -> None:
        self._count += a

    def _reset_count(self) -> None:
        self._count = 0

    @property
    def count(self) -> int:
        return self._count

    def __getattr__(self, rule_name: str) -> Any:
        if rule_name not in self._rule_map:
            raise AttributeError(rule_name)

        rule = (rule_item := self._rule_map[rule_name]).rule
        result = rule(current_count := self.count)
        self._add_count(rule_item.callback(current_count))
        return result

    def reset(self) -> None:
        for rule_item in self._rule_map.values():
            rule_item.rule.reset()
        self._reset_count()


__all__ = [
    "RuleEngine",
]
