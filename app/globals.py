from enum import Enum
from typing import TypeAlias

ScarabProfile: TypeAlias = dict[str, str | int]
ScarabConfig: TypeAlias = dict[str, list[ScarabProfile]]


class OutputMode(Enum):
    QUIET = 1
    NORMAL = 2


class ScarabException(Exception):
    pass


class ScarabError(ScarabException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ScarabOptionError(ScarabException):
    def __init__(self, message: str) -> None:
        super().__init__(f"Scarab got wrong or conflicting options: {message}")


class ScarabArgumentError(ScarabException):
    def __init__(self, message: str, option: str, argument: str) -> None:
        super().__init__(
            f"Scarab got invalid or conflicting arguments: {message}\n'{option}' is '{argument}'"
        )
