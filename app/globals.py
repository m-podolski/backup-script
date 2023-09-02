from enum import Enum


class OutputMode(Enum):
    QUIET = 1
    NORMAL = 2


class BackupMode(Enum):
    CREATE = "create"
    UPDATE = "update"


class ScarabException(Exception):
    pass


class ScarabOptionError(ScarabException):
    def __init__(self, message: str) -> None:
        super().__init__(f"Scarab got wrong or conflicting options: {message}")


class ScarabArgumentError(ScarabException):
    def __init__(self, message: str, option: str, argument: str) -> None:
        super().__init__(
            f"Scarab got invalid or conflicting arguments: {message}\n'{option}' is '{argument}'"
        )
