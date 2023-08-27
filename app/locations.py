import os
import re
from pathlib import Path
from typing import Literal, Optional, TypeAlias


class Location:
    _path: Path

    def __init__(self, path_arg: Optional[str]) -> None:
        if path_arg is None:
            self.path = Path()
        else:
            self.path = path_arg

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, path_arg: str | Path) -> None:
        expanded_user: str = os.path.expanduser(path_arg)
        expanded_vars: str = os.path.expandvars(expanded_user)
        self._path = Path(expanded_vars)

    @property
    def path_is_initialized(self) -> bool:
        """For the class to always provide a .path with all of Paths functionality available from the outside its default value has to be managed. This may be used to check if .path is actually set."""
        return not (str(self._path) == ".")

    @property
    def name(self) -> str:
        return self.__class__.__name__

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


class Destination(Location):
    MessageType: TypeAlias = Literal["NO_PATH_GIVEN"]
    messages: dict[MessageType, str] = {
        "NO_PATH_GIVEN": "Please specify a destination-path to the directory you want to back up to."
    }
