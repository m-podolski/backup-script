from enum import Enum, auto
from typing import Optional
from cement import Controller, ex, get_version  # pyright: ignore

from app.services.backup import (
    read_sourcepath,
    validate_sourcepath,
)  # pyright: ignore


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
                    "help": "Update an existig backup",
                    "action": "store_const",
                    "const": BackupMode.UPDATE,
                    "dest": "backup_mode",
                },
            ),
        ],
    )  # pyright: ignore
    def backup(self) -> None:
        print(self.app.pargs)  # pyright: ignore
        sourcepath: Optional[str] = self.app.pargs.sourcepath  # pyright: ignore
        if sourcepath is not None:
            validate_sourcepath(sourcepath)  # pyright: ignore
        else:
            read_sourcepath()
