import os
from pathlib import Path
from typing import Literal, Optional, TypeAlias

import app.io as io
from app.globals import OutputMode


class Location:
    _path: Optional[Path]

    def __init__(self, path_arg: Optional[str]) -> None:
        self.path = path_arg

    @property
    def path(self) -> Optional[Path]:
        return self._path

    @path.setter
    def path(self, path_arg: Optional[str]) -> None:
        match path_arg:
            case None:
                self._path = None
            case "":
                # Path converts empty strings to cwd by default
                self._path = None
            case _:
                expanded_user: str = os.path.expanduser(path_arg)
                expanded_vars: str = os.path.expandvars(expanded_user)
                self._path = Path(expanded_vars)

    @property
    def exists(self) -> bool:
        if self._path is None:
            return False
        return self._path.exists()

    @property
    def name(self) -> str:
        return self.__class__.__name__

    MessageType: TypeAlias = Literal["INVALID"]

    @property
    def common_messages(self) -> dict[MessageType, str]:
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


def check_path(
    location: Source | Destination, output_mode: OutputMode = OutputMode.NORMAL
) -> Source | Destination:
    if location.path is not None:
        if location.exists:
            return location
        else:
            path_in: str = io.read_path(
                location.common_messages["INVALID"],
                output_mode,
            )
            location.path = path_in
            return check_path(location, output_mode)
    else:
        path_in = io.read_path(location.messages["NO_PATH_GIVEN"], output_mode)
        location.path = path_in
        return check_path(location, output_mode)
