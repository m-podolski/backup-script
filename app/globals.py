from enum import Enum
from typing import Literal, TypeAlias

ScarabProfile: TypeAlias = dict[Literal["profile", "source", "target", "name"], str | int]
ScarabConfig: TypeAlias = dict[str, list[ScarabProfile]]


class BackupMode(Enum):
    AUTO = "Auto"
    CREATE = "Create"
    UPDATE = "Update"


class OutputMode(Enum):
    QUIET = 1
    NORMAL = 2
    AUTO = 3


class ScarabException(Exception):
    pass


class ScarabError(ScarabException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ScarabOptionError(ScarabException):
    message_prefix: str = "Scarab got wrong or conflicting options"

    def __init__(
        self,
        message: str,
        option: str,
    ) -> None:
        super().__init__(f"Scarab got wrong or conflicting options: {message}: '{option}'")


class ScarabArgumentError(ScarabException):
    def __init__(self, message: str, option: str, argument: str) -> None:
        super().__init__(f"Scarab got invalid arguments: {message}\n'{option}' is '{argument}'")
