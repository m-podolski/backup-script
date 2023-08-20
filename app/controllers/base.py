from enum import Enum, auto
import os
from pathlib import Path
from typing import Optional
from cement import Controller, ex, get_version  # pyright: ignore

from app.exceptions import ScarabArgumentError  # pyright: ignore


VERSION = (0, 5, 0, "alpha", 0)
VERSION_BANNER = """
scarab-backup v%s
""" % get_version(
    VERSION
)


class BackupMode(Enum):
    CREATE = auto()
    UPDATE = auto()


class PathType(Enum):
    SOURCE = "sourcepath"
    DEST = "destinationpath"


class Base(Controller):
    class Meta:  # pyright: ignore
        label = "base"
        arguments = [
            (["-v", "--version"], {"action": "version", "version": VERSION_BANNER}),
        ]

    def _default(self):
        self.app.args.print_help()  # pyright: ignore

    @ex(
        help="Back up from from a sourcepath to an external drive",
        arguments=[
            (
                ["-s", "--source"],
                {"help": "The sourcepath", "action": "store", "dest": "sourcepath"},
            ),
            (
                ["-d", "--dest"],
                {"help": "The destinationpath", "action": "store", "dest": "destpath"},
            ),
            (
                ["-c", "--create"],
                {
                    "help": "Create a new backup",
                    "action": "store_const",
                    "const": BackupMode.CREATE,
                    "dest": "backup_mode",
                },
            ),
            (
                ["-u", "--update"],
                {
                    "help": "Update an existing backup",
                    "action": "store_const",
                    "const": BackupMode.UPDATE,
                    "dest": "backup_mode",
                },
            ),
        ],
    )  # pyright: ignore
    def backup(self) -> None:
        sourcepath: Path = self._check_path(
            self.app.pargs.sourcepath, PathType.SOURCE  # pyright: ignore
        )
        destpath: Path = self._check_path(self.app.pargs.destpath, PathType.DEST)  # pyright: ignore

    def _check_path(self, path_string: Optional[str], type: PathType) -> Path:
        if path_string is not None:
            path_string = os.path.expanduser(path_string)
            path_string = os.path.expandvars(path_string)
            path = Path(path_string)
            if path.exists():
                return path
            else:
                path_in: str = self._read_sourcepath(
                    f"Your {type.value} is not a valid directory! Please check and enter it again."
                )
                return self._check_path(path_in, type)
        else:
            match type:
                case PathType.SOURCE:
                    msg: str = "Please specify a sourcepath to the directory you want backed up."
                case PathType.DEST:
                    msg = (
                        "Please specify a destinationpath to the directory you want to back up to."
                    )
            path_in = self._read_sourcepath(msg)
            return self._check_path(path_in, type)

    def _read_sourcepath(self, prompt_message: str) -> str:
        if self.app.quiet:  # pyright: ignore
            raise ScarabArgumentError("Cannot receive input in quiet mode")
        self.app.render(  # pyright: ignore
            {"message": prompt_message},
            "input_prompt.jinja2",
        )
        return input("Path: ")
