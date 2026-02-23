from typing import Iterable, Mapping

from ...types.plugin import Info, Item


def get_deps_table_from_info(infos: Iterable[Info]) -> dict[str, tuple[str, ...]]:
    return {
        info.metadata.id: tuple(
            dep.id
            for dep in info.metadata.dependent_plugins
        )
        for info in infos
    }


def get_deps_table_from_item(items: Iterable[Item]) -> dict[str, tuple[str, ...]]:
    return get_deps_table_from_info(item.info for item in items)


def topo_sort(deps_table: Mapping[str, tuple[str, ...]]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    result: list[str] = []

    ind_inf: dict[str, int] = {dep_id: len(deps) for dep_id, deps in deps_table.items()}
    for _ in range(len(ind_inf)):
        if not ind_inf:
            break

        comp_list: list[str] = []
        for id_, ind in ind_inf.items():
            if ind != 0:
                continue

            result.append(id_)
            for dep_id, deps in deps_table.items():
                if id_ not in deps:
                    continue

                ind_inf[dep_id] -= 1

            comp_list.append(id_)

        for id_ in comp_list:
            del ind_inf[id_]

    result.reverse()
    return tuple(result), tuple(ind_inf.keys())


def _get_calc_deps(positive: bool, plugin_id: str, deps_table: Mapping[str, tuple[str, ...]]) -> set[str]:
    if positive:
        return {ldep_id for ldep_id in deps_table.get(plugin_id, ())}
    else:
        return {rdep_id for rdep_id, dep_list in deps_table.items() if plugin_id in dep_list}

def _get_deps_plugin(positive: bool, plugin_id: str, deps_table: Mapping[str, tuple[str, ...]]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    visited_list: set[str] = {plugin_id}
    deps_id: set[str] = {plugin_id}
    stack: list[str] = [plugin_id]

    while stack:
        current_id = stack.pop()
        current_deps = _get_calc_deps(positive, current_id, deps_table)
        deps_id.update(current_deps)

        for dep_id in current_deps:
            if dep_id in visited_list:
                continue

            visited_list.add(dep_id)
            stack.append(dep_id)

    sub_deps_info: dict[str, tuple[str, ...]] = {}
    for dep_id, deps in deps_table.items():
        if dep_id not in deps_id:
            continue

        sub_deps_info[dep_id] = tuple(id_ for id_ in deps if id_ in deps_id)

    return topo_sort(sub_deps_info)


def get_ldeps_plugin(plugin_id: str, deps_table: Mapping[str, tuple[str, ...]]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return _get_deps_plugin(True, plugin_id, deps_table)


def get_rdeps_plugin(plugin_id: str, deps_table: Mapping[str, tuple[str, ...]]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    result = _get_deps_plugin(False, plugin_id, deps_table)
    return result[0][::-1], result[1]


__all__ = [
    "get_deps_table_from_info",
    "get_deps_table_from_item",
    "topo_sort",
    "get_ldeps_plugin",
    "get_rdeps_plugin",
]
