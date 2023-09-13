from dataclasses import dataclass
import datetime
import os
from pathlib import Path
import socket
from typing import Literal, Optional, TypeAlias


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


class NameFormats(ScarabRecord):
    _source: str

    def __init__(
        self,
        source: str,
    ) -> None:
        self._source = source

    @property
    def name_formats(self) -> list[str]:
        return list(self._map_formats().keys())

    def select(self, option: int) -> str:
        return list(self._map_formats().values())[option - 1]

    def _map_formats(self) -> dict[str, str]:
        user: str = os.environ["USER"]
        host: str = socket.gethostname()
        date: str = datetime.datetime.today().strftime("%Y-%m-%d")
        time: str = datetime.datetime.today().strftime("%H-%M-%S")

        return {
            "<source-dir>": self._source,
            "<source-dir>_<date>": f"{self._source}_{date}",
            "<source-dir>_<date-time>": f"{self._source}_{date}-{time}",
            "<user>@<host>_<source-dir>": f"{user}@{host}_{self._source}",
            "<user>@<host>_<source-dir>_<date>": f"{user}@{host}_{self._source}_{date}",
            "<user>@<host>_<source-dir>_<date-time>": f"{user}@{host}_{self._source}_{date}-{time}",
        }
