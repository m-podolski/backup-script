from enum import Enum
from typing import Optional

from cement import Controller, ex, get_version  # pyright: ignore

import app.locations as locations
from app.exceptions import ScarabOptionError  # pyright: ignore
from app.globals import OutputMode
from app.locations import Destination, Location, Source

VERSION: tuple[int, int, int, str, int] = (0, 5, 0, "alpha", 0)
VERSION_BANNER = """
scarab-backup v%s
""" % get_version(
    VERSION
)


class BackupMode(Enum):
    CREATE = 1
    UPDATE = 2


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
                {"help": "The sourcepath", "action": "store", "dest": "source"},
            ),
            (
                ["-d", "--dest"],
                {"help": "The destinationpath", "action": "store", "dest": "dest"},
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
        quiet: bool = self.app.quiet  # pyright: ignore
        source_arg: Optional[str] = self.app.pargs.source  # pyright: ignore
        dest_arg: Optional[str] = self.app.pargs.dest  # pyright: ignore

        if quiet:
            output_mode = OutputMode.QUIET
        else:
            output_mode = OutputMode.NORMAL

        source: Location = locations.check_path(Source(source_arg), output_mode)  # pyright: ignore
        destination: Location = locations.check_path(
            Destination(dest_arg), output_mode  # pyright: ignore
        )

        print({"source": str(source.path), "dest": str(destination.path)})  # pyright: ignore
