import os
import re
from pathlib import Path
from re import Match
from typing import Optional


class Location:
    _path: Path

    def __init__(self, path_arg: str | Path) -> None:
        self.path = path_arg

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, path_arg: str | Path) -> None:
        if isinstance(path_arg, str):
            if path_arg == "":
                self._path = Path()
                return

            path_exp_user: str = os.path.expanduser(path_arg)
            path_exp_vars: str = os.path.expandvars(path_exp_user)

            self._path = Path(path_exp_vars).resolve()

        if isinstance(path_arg, Path):
            self._path = path_arg

    @property
    def is_valid(self) -> bool:
        """
        Checks if ._path is initialized properly and not using its default value (i.e. for empty strings).
        """
        if str(self._path) == ".":
            return False
        return self._path.is_dir()

    @property
    def is_media_dir(self) -> bool:
        is_media_dir: bool = re.match(r"^/media/.+", str(self._path)) is not None
        is_test_temp_media_dir: bool = (
            re.match(r"^/tmp/pytest.+media$", str(self._path)) is not None
        )
        return is_media_dir or is_test_temp_media_dir

    @property
    def name(self) -> str:
        return self.__class__.__name__


class Source(Location):
    pass


class Target(Location):
    existing_backup: Optional[Path] = None

    backup_name: Optional[str] = None

    @property
    def path(self) -> Path:
        return super().path

    @path.setter
    def path(self, path_arg: str | Path) -> None:
        Location.path.fset(self, path_arg)
        if self.is_valid:
            self._path = self._get_contained_backup_dir(self._path)

    def _get_contained_backup_dir(self, path: Path) -> Path:
        matches: list[str] = sorted(
            [str(path) for path in path.iterdir() if self._matches_backup_dir(path)]
        )
        if len(matches) > 0:
            return path / matches[0]
        return path

    def _matches_backup_dir(self, item: Path) -> bool:
        match: Match[str] | None = re.match(r".+/[Bb]ackup[s]*$", str(item))
        return match is not None and item.is_dir()

    @property
    def content(self) -> list[str]:
        directory: Path
        if self.existing_backup is not None:
            directory = self.existing_backup
        else:
            directory = self._path
        return sorted([self._add_slash_to_dir(path) for path in directory.iterdir()])

    def _add_slash_to_dir(self, path: Path) -> str:
        if path.is_dir():
            return f"{path.name}/"
        else:
            return path.name

    @property
    def content_dirs(self) -> list[str]:
        return sorted(
            [item[0 : len(item) - 1 :] for item in self.content if item[len(item) - 1] == "/"]
        )
