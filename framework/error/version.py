class VersionError(Exception):
    pass


class InvalidVersionValueError(VersionError):
    def __init__(self, version):
        super().__init__(f"invalid version: <{version}>")


class InvalidVersionOperationError(VersionError):
    def __init__(self):
        super().__init__("cannot compare wildcard version")


__all__ = [
    "VersionError",
    "InvalidVersionValueError",
    "InvalidVersionOperationError",
]
