import os
from typing import Optional

from cement import Controller, ex, get_version  # pyright: ignore

import app.interactions as interactions
import app.io as appio
from app.globals import BackupMode, OutputMode, ScarabOptionError
from app.locations import Location, Source, Target

VERSION: tuple[int, int, int, str, int] = (0, 5, 0, "alpha", 0)
VERSION_BANNER: str = """
scarab-backup v%s
""" % get_version(
    VERSION
)


class Base(Controller):
    class Meta:  # pyright: ignore
        label: str = "base"
        arguments: list[tuple[list[str], dict[str, str]]] = [
            (["-v", "--version"], {"action": "version", "version": VERSION_BANNER}),
        ]

    def _default(self) -> None:
        self.app.args.print_help()  # pyright: ignore

    @ex(
        help="Back up from from a sourcepath to an external drive",
        arguments=[
            (
                ["-s", "--source"],
                {"help": "The source-path", "action": "store", "dest": "source"},
            ),
            (
                ["-t", "--target"],
                {"help": "The target-path", "action": "store", "dest": "target"},
            ),
            (
                ["-m", "--media"],
                {
                    "help": "Select your media-directory as target",
                    "action": "store_const",
                    "const": f"/media/{os.environ['USER']}",
                    "dest": "target",
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
        target_arg: Optional[str] = self.app.pargs.target  # pyright: ignore
        backup_mode: Optional[BackupMode] = self.app.pargs.backup_mode  # pyright: ignore

        if quiet:
            output_mode = OutputMode.QUIET
        else:
            output_mode = OutputMode.NORMAL

        source: Location = interactions.check_path(
            Source(source_arg), output_mode  # pyright: ignore
        )
        target: Location = interactions.check_path(
            Target(target_arg), output_mode  # pyright: ignore
        )

        if target.is_media_dir:
            target = interactions.select_media_dir(source, target, output_mode)

        if backup_mode is None:  # pyright: ignore [reportUnnecessaryComparison]
            backup_mode: BackupMode = interactions.select_backup_mode(output_mode)

        if backup_mode is BackupMode.UPDATE:
            target.path = interactions.select_target_directory(target, output_mode)

        target_name: str = interactions.select_target_name(source.path.name, output_mode)

        if source.path == target.path:
            raise ScarabOptionError("Source and target are identical")

        appio.render(
            "target_contents.jinja2",
            {
                "source": str(source.path),
                "target": str(target.path),
                "backup_mode": backup_mode.value.title(),
                "target_name": target_name,
                "target_content": target.content,
            },
        )
