from enum import Enum, auto
from typing import Optional
from cement import Controller, ex, get_version  # pyright: ignore

from app.services.backup import (
    validate_sourcepath,
)


VERSION = (0, 5, 0, "alpha", 0)
VERSION_BANNER = """
scarab-backup v%s
""" % get_version(
    VERSION
)


class BackupMode(Enum):
    CREATE = auto()
    UPDATE = auto()


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
        checked_sourcepath: str = self._check_sourcepath(
            self.app.pargs.sourcepath  # pyright: ignore
        )
        print(checked_sourcepath)

    def _check_sourcepath(self, path: Optional[str]) -> str:
        if path is not None:
            valid_path: Optional[str] = validate_sourcepath(path)
            if valid_path:
                return valid_path
            else:
                path_in: str = self._read_sourcepath(
                    "Your sourcepath is not a valid directory! Please check and enter it again."
                )
                return self._check_sourcepath(path_in)
        else:
            path_in = self._read_sourcepath(
                "Please specify a sourcepath to the directory you want backed up."
            )
            return self._check_sourcepath(path_in)

    def _read_sourcepath(self, prompt_message: str) -> str:
        self.app.render(  # pyright: ignore
            {"message": prompt_message},
            "input_prompt.jinja2",
        )
        return input("Path: ")
