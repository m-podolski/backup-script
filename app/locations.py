from enum import Enum
import os
from pathlib import Path
from typing import Optional
from app.globals import OutputMode

import app.io as io


class PathType(Enum):
    SOURCE = "sourcepath"
    DEST = "destinationpath"


def check_path(path_string: Optional[str], type: PathType, output_mode: OutputMode) -> Path:
    if path_string is not None:
        path_string = os.path.expanduser(path_string)
        path_string = os.path.expandvars(path_string)
        path = Path(path_string)
        if path.exists():
            return path
        else:
            path_in: str = io.read_path(
                f"Your {type.value} is not a valid directory! Please check and enter it again.",
                output_mode,
            )
            return check_path(path_in, type, output_mode)
    else:
        match type:
            case PathType.SOURCE:
                msg: str = "Please specify a sourcepath to the directory you want backed up."
            case PathType.DEST:
                msg = "Please specify a destinationpath to the directory you want to back up to."
        path_in = io.read_path(msg, output_mode)
        return check_path(path_in, type, output_mode)
