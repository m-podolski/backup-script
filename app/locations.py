import os
import re
from pathlib import Path
from re import Match
from typing import Literal, Optional, TypeAlias


class Location:
    _path: Path

    def __init__(self, path_arg: Optional[str | Path]) -> None:
        if path_arg is None:
            self.path = Path()
        else:
            self.path = path_arg

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, path_arg: str | Path) -> None:
        if isinstance(path_arg, str):
            path_exp_user: str = os.path.expanduser(path_arg)
            path_exp_vars: str = os.path.expandvars(path_exp_user)

            # probably from input, so empty strings must be handled
            is_longer_0: bool = len(path_exp_vars) > 0
            starts_with_dot: bool = path_exp_vars[0] == "." if is_longer_0 else False

            if is_longer_0 and starts_with_dot:
                self._path = Path(path_exp_vars).resolve()
            else:
                self._path = Path(path_exp_vars)

        if isinstance(path_arg, Path):
            self._path = path_arg

    @property
    def path_is_initialized(self) -> bool:
        """
        For the class to always provide a .path with all of Paths functionality available from the outside its default value has to be managed. This may be used to check if .path is actually set.
        """
        return not (str(self._path) == ".")

    @property
    def exists(self) -> bool:
        if not self.path_is_initialized:
            return False
        return self._path.exists()

    @property
    def is_media_dir(self) -> bool:
        if not self.path_is_initialized:
            return False
        is_media_dir: bool = re.match(r"^/media/.+", str(self._path)) is not None
        is_test_temp_media_dir: bool = (
            re.match(r"^/tmp/pytest.+media$", str(self._path)) is not None
        )
        return is_media_dir or is_test_temp_media_dir

    @property
    def content(self) -> list[str]:
        if not self.path_is_initialized:
            return []
        return sorted([self._add_slash_to_dir(path) for path in self._path.iterdir()])

    def _add_slash_to_dir(self, path: Path) -> str:
        if path.is_dir():
            return f"{path.name}/"
        else:
            return path.name

    @property
    def name(self) -> str:
        return self.__class__.__name__

    MessageType: TypeAlias = Literal["INVALID"]

    @property
    def location_messages(self) -> dict[MessageType, str]:
        return {
            "INVALID": f"Your {self.name.lower()} is not a valid directory! Please check and enter it again."
        }


class Source(Location):
    MessageType: TypeAlias = Literal["NO_PATH_GIVEN"]
    messages: dict[MessageType, str] = {
        "NO_PATH_GIVEN": "Please specify a source-path to the directory you want backed up."
    }


class Target(Location):
    @property
    def path(self) -> Path:
        return super().path

    @path.setter
    def path(self, path_arg: str | Path) -> None:
        Location.path.fset(self, path_arg)
        if self.exists:
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

    MessageType: TypeAlias = Literal["NO_PATH_GIVEN"]
    messages: dict[MessageType, str] = {
        "NO_PATH_GIVEN": "Please specify a target-path to the directory you want to back up to."
    }
