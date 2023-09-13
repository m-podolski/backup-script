from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal, Optional, TypeAlias

ScarabProfile: TypeAlias = dict[Literal["profile", "source", "target", "name"], str | int]
ScarabConfig: TypeAlias = dict[str, list[ScarabProfile]]


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
    def __init__(self, message: str) -> None:
        super().__init__(f"Scarab got wrong or conflicting options: {message}")


class ScarabArgumentError(ScarabException):
    def __init__(self, message: str, option: str, argument: str) -> None:
        super().__init__(f"Scarab got invalid arguments: {message}\n'{option}' is '{argument}'")


@dataclass
class ScarabRecord:
    pass


@dataclass(init=True, repr=True)
class ScarabMessage(ScarabRecord):
    message: str


BackupMode: TypeAlias = Literal["Auto", "Create", "Update"]


@dataclass(repr=True)
class BackupParams(ScarabRecord):
    backup_mode: BackupMode
    source: str
    target: str
    existing_backup: Optional[str]
    backup_name: str

    def __init__(
        self,
        backup_mode: BackupMode,
        source: Path,
        target: Path,
        existing_backup: Optional[Path],
        backup_name: str,
    ) -> None:
        self.backup_mode = backup_mode
        self.source = str(source)
        self.target = str(target)
        self.existing_backup = str(existing_backup.name) if existing_backup else None
        self.backup_name = backup_name


@dataclass(repr=True)
class TargetContent(ScarabRecord):
    target_content: list[str]
    source: Optional[str]
    target: Optional[str]

    def __init__(
        self,
        target_content: list[str],
        source: Optional[Path] = None,
        target: Optional[Path] = None,
    ) -> None:
        self.source = str(source)
        self.target = str(target)
        self.target_content = target_content


@dataclass(repr=True)
class NameFormats(ScarabRecord):
    # name_formats: list[str]
    name_formats: tuple[str, ...] = (
        "<source-dir>",
        "<source-dir>_<date>",
        "<source-dir>_<date-time>",
        "<user>@<host>_<source-dir>",
        "<user>@<host>_<source-dir>_<date>",
        "<user>@<host>_<source-dir>_<date-time>",
    )

