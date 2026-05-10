"""
Dependency table: Mapping[ID, All IDs depended on by this ID]
"""

from functools import wraps
from typing import Callable, Concatenate, Iterable, Mapping, ParamSpec, TypeVar


_DEPENDENCY_TABLE = Mapping[str, Iterable[str]]
_FORMATTED_DEPENDENCY_TABLE = dict[str, set[str]]
_P = ParamSpec("ParamSpec")
_R = TypeVar("_R")


def _format_dependency_table(dependency_table: _DEPENDENCY_TABLE) -> _FORMATTED_DEPENDENCY_TABLE:
    return {k: set(v) for k, v in dependency_table.items()}


def _auto_formatter(func: Callable[Concatenate[_FORMATTED_DEPENDENCY_TABLE, _P], _R]) -> Callable[Concatenate[_DEPENDENCY_TABLE, _P], _R]:
    @wraps(func)
    def wrapped(dependency_table: _DEPENDENCY_TABLE, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        return func(_format_dependency_table(dependency_table), *args, **kwargs)
    return wrapped


@_auto_formatter
def get_missing_dependencies(dependency_table: _FORMATTED_DEPENDENCY_TABLE, identifier: str) -> set[str]:
    dependencies = dependency_table.get(identifier, set())
    return {dependency for dependency in dependencies if dependency not in dependency_table}


@_auto_formatter
def check_dependency_integrity(dependency_table: _FORMATTED_DEPENDENCY_TABLE) -> dict[str, set[str]]:
    return {
        id_: missing
        for id_ in dependency_table.keys()
        if (missing := get_missing_dependencies(dependency_table, id_))
    }


@_auto_formatter
def gen_reverse_dependency_table(dependency_table: _FORMATTED_DEPENDENCY_TABLE) -> _FORMATTED_DEPENDENCY_TABLE:
    reverse_dependency_table: dict[str, set[str]] = {}
    for id_, dependencies in dependency_table.items():
        for dependency in dependencies:
            reverse_dependency_table.setdefault(dependency, set()).add(id_)
    return reverse_dependency_table


@_auto_formatter
def gen_priority_list(dependency_table: _FORMATTED_DEPENDENCY_TABLE) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """
    Generate a list of dependency priorities according to the dependency table. \n
    The first return value is a list sorted from high to low according to dependency priority, and the second return value is an item with circular dependency.
    """
    priority_list: list[str] = []

    task_table = dict(dependency_table)
    reverse_dependency_table = gen_reverse_dependency_table(dependency_table)
    finished_stack = [id_ for id_, dependencies in task_table.items() if not dependencies]
    while finished_stack:
        current_finished = finished_stack.pop()
        priority_list.append(current_finished)
        task_table.pop(current_finished)

        if current_finished not in reverse_dependency_table:
            continue
        for reverse_dependency in reverse_dependency_table[current_finished]:
            (dependencies := task_table[reverse_dependency]).remove(current_finished)
            if not dependencies:
                finished_stack.append(reverse_dependency)

    return tuple(priority_list), tuple(task_table.keys())


@_auto_formatter
def _get_dependencies_getter(
        dependency_table: _FORMATTED_DEPENDENCY_TABLE,
        reverse: bool = False,
) -> Callable[[str], set[str]]:
    if reverse:
        reverse_dependency_table = gen_reverse_dependency_table(dependency_table)
        getter = lambda id_: reverse_dependency_table.get(id_, set())
    else:
        getter = lambda id_: set(dependency_table.get(id_, set()))
    return getter


@_auto_formatter
def _gen_sub_dependency_table(
        dependency_table: _FORMATTED_DEPENDENCY_TABLE,
        identifier: str,
        reverse: bool = False,
) -> _FORMATTED_DEPENDENCY_TABLE:
    visited = {identifier}
    full_dependencies = {identifier}
    dependencies_getter = _get_dependencies_getter(dependency_table, reverse)

    id_stack = [identifier]
    while id_stack:
        current_id = id_stack.pop()
        current_dependencies = dependencies_getter(current_id)
        full_dependencies.update(current_dependencies)

        for dependency in current_dependencies:
            if dependency in visited:
                continue
            visited.add(dependency)
            id_stack.append(dependency)

    return {
        id_: {dependency for dependency in dependencies if dependency in full_dependencies}
        for id_, dependencies in dependency_table.items()
        if id_ in full_dependencies
    }


@_auto_formatter
def gen_priority_list_by_forward_dependency(
        dependency_table: _FORMATTED_DEPENDENCY_TABLE,
        identifier: str,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return gen_priority_list(_gen_sub_dependency_table(dependency_table, identifier, False))


@_auto_formatter
def gen_priority_list_by_reverse_dependency(
        dependency_table: _FORMATTED_DEPENDENCY_TABLE,
        identifier: str,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return gen_priority_list(_gen_sub_dependency_table(dependency_table, identifier, True))


__all__ = [
    "get_missing_dependencies",
    "check_dependency_integrity",
    "gen_reverse_dependency_table",
    "gen_priority_list",
    "gen_priority_list_by_forward_dependency",
    "gen_priority_list_by_reverse_dependency",
]
