from ..error.version import InvalidVersionValueError, InvalidVersionOperationError

from typing import Union


class Version:
    def __init__(self, v_str: str):
        if not isinstance(v_str, str):
            raise InvalidVersionValueError(v_str)

        self._has_wildcard = False

        version = v_str.split(".")
        if len(version) == 2:
            version.append("*")
        if len(version) != 3:
            raise InvalidVersionValueError(version)

        try:
            self.major = int(version[0])
            self.minor = int(version[1])
            self.patch = "*" if version[2] == "*" else int(version[2])

        except ValueError:
            raise InvalidVersionValueError(version)

        if self.patch == "*":
            self._has_wildcard = True

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self):
        return f"{self.__class__.__name__}(\'{self.__str__()}\')"

    @property
    def has_wildcard(self) -> bool:
        return self._has_wildcard

    def satisfies(self, condition: Union[str, "Version", None]) -> bool:
        if self._has_wildcard:
            raise InvalidVersionOperationError()

        if condition is None:
            return True

        if isinstance(condition, str):
            condition = Version(condition)
        if self.major != condition.major:
            return False
        if self.minor != condition.minor:
            return False
        if condition._has_wildcard:
            return True
        return self.patch == condition.patch

    def _check_mm(self, condition: Union[str, "Version", None], m: bool) -> bool:
        if self._has_wildcard:
            raise InvalidVersionOperationError()

        if not condition:
            return True
        if isinstance(condition, str):
            condition = Version(condition)
        if self.major < condition.major:
            return False != m
        if self.major > condition.major:
            return True != m
        if self.minor < condition.minor:
            return False != m
        if self.minor > condition.minor:
            return True != m
        if condition._has_wildcard:
            return True
        if m:
            return self.patch <= condition.patch
        return self.patch >= condition.patch

    def in_range(self, min_condition: Union[str, "Version", None], max_condition: Union[str, "Version", None]) -> bool:
        return self._check_mm(min_condition, False) and self._check_mm(max_condition, True)

    def auto_check(self, versions: tuple[Union[str, "Version", None], ...]) -> bool:
        ver_len = len(versions)
        if ver_len == 0:
            return True
        elif ver_len == 1:
            return self.satisfies(versions[0])
        elif ver_len == 2:
            return self.in_range(versions[0], versions[1])
        return False


__all__ = [
    "Version",
]
