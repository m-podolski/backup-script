import os
from enum import Enum
from typing import Optional

from cement import Controller, ex, get_version  # pyright: ignore

import app.interactions as interactions
import app.io as appio
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
                {"help": "The source-path", "action": "store", "dest": "source"},
            ),
            (
                ["-d", "--dest"],
                {"help": "The destination-path", "action": "store", "dest": "dest"},
            ),
            (
                ["-m", "--media"],
                {
                    "help": "Select your media-directory as destination",
                    "action": "store_const",
                    "const": f"/media/{os.environ['USER']}",
                    "dest": "media",
                },
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
        media_arg: Optional[str] = self.app.pargs.media  # pyright: ignore

        if quiet:
            output_mode = OutputMode.QUIET
        else:
            output_mode = OutputMode.NORMAL

        source: Location = interactions.check_path(
            Source(source_arg), output_mode  # pyright: ignore
        )
        destination: Location = interactions.check_path(
            Destination(dest_arg), output_mode  # pyright: ignore
        )

        if destination.is_media_dir:
            destination = interactions.select_media_dir(source, destination, output_mode)
        else:
            appio.render(
                "dest_contents.jinja2",
                {
                    "source": str(source.path),
                    "destination": str(destination.path),
                    "destination_content": destination.content,
                },
            )
