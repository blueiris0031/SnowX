from typing import Callable, Iterable, Mapping

from ...types.plugin import Info, Item


def gen_dependency_table_from_info_list(info_list: Iterable[Info]) -> dict[str, set[str]]:
    return {info.metadata.id: {dependent_plugin.id for dependent_plugin in info.metadata.dependent_plugins} for info in info_list}


def gen_dependency_table_from_item_list(item_list: Iterable[Item]) -> dict[str, set[str]]:
    return gen_dependency_table_from_info_list(item.info for item in item_list)


def get_missing_dependencies(identifier: str, dependency_table: Mapping[str, set[str]]) -> set[str]:
    dependencies = dependency_table.get(identifier, set())
    return {dependency for dependency in dependencies if dependency not in dependency_table}


def check_dependency_integrity(dependency_table: Mapping[str, set[str]]) -> dict[str, set[str]]:
    return {
        id_: missing
        for id_ in dependency_table.keys()
        if (missing := get_missing_dependencies(id_, dependency_table))
    }


def gen_reverse_dependency_table(dependency_table: Mapping[str, set[str]]) -> dict[str, set[str]]:
    reverse_dependency_table: dict[str, set[str]] = {}
    for id_, dependencies in dependency_table.items():
        for dependency in dependencies:
            reverse_dependency_table.setdefault(dependency, set()).add(id_)
    return reverse_dependency_table


def gen_priority_list(dependency_table: Mapping[str, set[str]]) -> tuple[tuple[str, ...], tuple[str, ...]]:
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


def _get_dependencies_getter(dependency_table: Mapping[str, set[str]], reverse: bool = False) -> Callable[[str], set[str]]:
    if reverse:
        reverse_dependency_table = gen_reverse_dependency_table(dependency_table)
        def reverse_getter(identifier: str) -> set[str]:
            return reverse_dependency_table.get(identifier, set())
        return reverse_getter
    def forward_getter(identifier: str) -> set[str]:
        return set(dependency_table.get(identifier, set()))
    return forward_getter


def _gen_sub_dependency_table(identifier: str, dependency_table: Mapping[str, set[str]], reverse: bool = False) -> dict[str, set[str]]:
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


def gen_priority_list_by_forward_dependency(identifier: str, dependency_table: Mapping[str, set[str]]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return gen_priority_list(_gen_sub_dependency_table(identifier, dependency_table, False))


def gen_priority_list_by_reverse_dependency(identifier: str, dependency_table: Mapping[str, set[str]]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return gen_priority_list(_gen_sub_dependency_table(identifier, dependency_table, True))


__all__ = [
    "gen_dependency_table_from_info_list",
    "gen_dependency_table_from_item_list",
    "get_missing_dependencies",
    "check_dependency_integrity",
    "gen_reverse_dependency_table",
    "gen_priority_list",
    "gen_priority_list_by_forward_dependency",
    "gen_priority_list_by_reverse_dependency",
]
