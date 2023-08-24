import os
from enum import Enum
from pathlib import Path
from typing import Literal, Optional, TypeAlias

import app.io as io
from app.globals import OutputMode


class PathType(Enum):
    SOURCE = "sourcepath"
    DEST = "destinationpath"


class Location:
    path: Optional[Path]

    def __init__(self, path_arg: Optional[str]) -> None:
        if path_arg is None:
            self.path = None
        else:
            expanded_user: str = os.path.expanduser(path_arg)
            expanded_vars: str = os.path.expandvars(expanded_user)
            self.path = Path(expanded_vars)

    @property
    def exists(self) -> bool:
        if self.path is None:
            return False
        return self.path.exists()

    @property
    def name(self) -> str:
        return self.__class__.__name__

    MessageType: TypeAlias = Literal["INVALID"]

    @property
    def common_messages(self) -> dict[MessageType, str]:
        return {
            "INVALID": f"Your {self.name} is not a valid directory! Please check and enter it again."
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


def check_path(path_arg: Optional[str], type: PathType, output_mode: OutputMode) -> Location:
    location: Location
    match type:
        case PathType.SOURCE:
            location = Source(path_arg)
        case PathType.DEST:
            location = Destination(path_arg)

    if location.path is not None:
        if location.exists:
            return location
        else:
            path_in: str = io.read_path(
                location.common_messages["INVALID"],
                output_mode,
            )
            return check_path(path_in, type, output_mode)
    else:
        path_in = io.read_path(location.messages["NO_PATH_GIVEN"], output_mode)
        return check_path(path_in, type, output_mode)
