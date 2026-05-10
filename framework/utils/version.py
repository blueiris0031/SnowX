from functools import lru_cache
from typing import Literal
from warnings import warn
from weakref import WeakValueDictionary


class VersionError(Exception):
    pass


class InvalidVersionValueError(VersionError):
    def __init__(self, version_str: str):
        super().__init__(f"invalid version: <{version_str}>")


class InvalidVersionOperationError(VersionError):
    def __init__(self):
        super().__init__("cannot compare wildcard version")


class VersionWarning(UserWarning):
    pass


class VersionInheritanceWarning(VersionWarning):
    pass


_WILDCARD_TYPE = Literal["*"]
_WILDCARD: _WILDCARD_TYPE = "*"
_WILDCARD_INFO_TYPE = tuple[Literal[True], _WILDCARD_TYPE]
_WILDCARD_INFO: _WILDCARD_INFO_TYPE = (True, _WILDCARD)
_VERSION_INFO_TYPE = tuple[int, Literal[False]] | _WILDCARD_INFO_TYPE


class Version:
    def __init_subclass__(cls) -> None:
        warn("Subclass inheritance is not recommended", VersionInheritanceWarning)

    @staticmethod
    def _conv_int(string: str) -> int:
        if (r:= int(string)) < 0:
            raise ValueError
        return r

    @classmethod
    @lru_cache(maxsize=32)
    def _analysis_str(cls, version_str: str) -> tuple[_VERSION_INFO_TYPE, _VERSION_INFO_TYPE, _VERSION_INFO_TYPE]:
        version_list = version_str.split(".")
        for x in range(3 - len(version_list)):
            version_list.append(_WILDCARD)
        if len(version_list) > 3:
            raise InvalidVersionValueError(version_str)

        raw_major, raw_minor, raw_patch = version_list
        (
            major_is_wildcard,
            minor_is_wildcard,
            patch_is_wildcard,
        ) = (
            raw_major == _WILDCARD,
            raw_minor == _WILDCARD,
            raw_patch == _WILDCARD,
        )
        if major_is_wildcard and not minor_is_wildcard:
            raise InvalidVersionValueError(version_str)
        if minor_is_wildcard and not patch_is_wildcard:
            raise InvalidVersionValueError(version_str)
        try:
            return (
                _WILDCARD_INFO if major_is_wildcard else (cls._conv_int(raw_major), False),
                _WILDCARD_INFO if minor_is_wildcard else (cls._conv_int(raw_minor), False),
                _WILDCARD_INFO if patch_is_wildcard else (cls._conv_int(raw_patch), False),
            )
        except ValueError:
            raise InvalidVersionValueError(version_str)

    def __new__(cls, version_str: str):
        formatted_version_str = ".".join(str(v[0]) for v in cls._analysis_str(version_str))
        if not hasattr(cls, "_instance_map"):
            cls._instance_map = WeakValueDictionary()
        instance_map: WeakValueDictionary[str, "Version"] = getattr(cls, "_instance_map")

        if formatted_version_str not in instance_map:
            new_instance = super().__new__(cls)
            new_instance._is_inited = False
            instance_map[formatted_version_str] = new_instance
        return instance_map[formatted_version_str]

    def __init__(self, version_str: str) -> None:
        if self._is_inited:
            return
        self._real_init(version_str)
        self._is_inited = True

    def _real_init(self, version_str: str) -> None:
        self._major, self._minor, self._patch = self._analysis_str(version_str)
        self._has_wildcard = self._major[1] or self._minor[1] or self._patch[1]

    def __str__(self) -> str:
        return f"{self._major[0]}.{self._minor[0]}.{self._patch[0]}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(\'{self.__str__()}\')"

    def __hash__(self) -> int:
        return hash(self.__str__())

    @property
    def major(self) -> _VERSION_INFO_TYPE:
        return self._major

    @property
    def minor(self) -> _VERSION_INFO_TYPE:
        return self._minor

    @property
    def patch(self) -> _VERSION_INFO_TYPE:
        return self._patch

    @property
    def has_wildcard(self) -> bool:
        return self._has_wildcard

    def __contains__(self, version: "Version") -> bool:
        if version.has_wildcard:
            raise InvalidVersionOperationError
        if self._major[1]:
            return True
        if self._major[0] != version.major[0]:
            return False
        if self._minor[1]:
            return True
        if self._minor[0] != version.minor[0]:
            return False
        if self._patch[1]:
            return True
        if self._patch[0] != version.patch[0]:
            return False
        return True

    def __eq__(self, version: "Version") -> bool:
        return self is version

    def __lt__(self, version: "Version") -> bool:
        if self.has_wildcard or version.has_wildcard:
            raise InvalidVersionOperationError
        if self._major[0] != version.major[0]:
            return self._major[0] < version.major[0]
        if self._minor[0] != version.minor[0]:
            return self._minor[0] < version.minor[0]
        if self._patch[0] != version.patch[0]:
            return self._patch[0] < version.patch[0]
        return False

    def __le__(self, version: "Version") -> bool:
        return self.__eq__(version) or self.__lt__(version)

    def __gt__(self, version: "Version") -> bool:
        return not self.__le__(version)

    def __ge__(self, version: "Version") -> bool:
        return not self.__lt__(version)


__all__ = [
    "VersionError",
    "InvalidVersionValueError",
    "InvalidVersionOperationError",
    "VersionWarning",
    "VersionInheritanceWarning",
    "Version",
]
