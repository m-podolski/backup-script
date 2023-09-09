import os
from typing import Optional

from cement import Controller, ex, get_version  # pyright: ignore

import app.config as config
import app.interactions as interactions
import app.io as io
from app.globals import BackupMode, OutputMode, ScarabArgumentError
from app.locations import Source, Target

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
            (
                ["-n", "--name"],
                {
                    "help": """The name-format for your backup (1..6)
                        1: <source-dir>,
                        2: <source-dir>_<date>
                        3: <source-dir>_<date-time>
                        4: <user>@<host>_<source-dir>
                        5: <user>@<host>_<source-dir>_<date>
                        6: <user>@<host>_<source-dir>_<date-time>""",
                    "action": "store",
                    "dest": "name",
                },
            ),
        ],
    )  # pyright: ignore
    def backup(self) -> None:
        quiet: bool = self.app.quiet  # pyright: ignore
        source_arg: Optional[str] = self.app.pargs.source  # pyright: ignore
        target_arg: Optional[str] = self.app.pargs.target  # pyright: ignore
        backup_mode: Optional[BackupMode] = self.app.pargs.backup_mode  # pyright: ignore
        name_arg: Optional[str] = self.app.pargs.name  # pyright: ignore

        if quiet:
            output_mode = OutputMode.QUIET
        else:
            output_mode = OutputMode.NORMAL

        source: Source = interactions.init_location(
            source_arg, Source, output_mode  # pyright: ignore
        )
        target: Target = interactions.init_location(
            target_arg, Target, output_mode  # pyright: ignore
        )

        if target.is_media_dir:
            target = interactions.select_media_dir(source, target, output_mode)

        if backup_mode is None:  # pyright: ignore [reportUnnecessaryComparison]
            backup_mode: BackupMode = interactions.select_backup_mode(output_mode)

        if backup_mode is BackupMode.UPDATE:
            target.existing_backup = interactions.select_backup_directory(target, output_mode)

        if source.path == target.existing_backup:
            raise ScarabArgumentError(
                "Source is the selected existing backup-directory", "source", str(source.path)
            )

        target.backup_name = interactions.select_backup_name(
            source,
            target,
            backup_mode,
            name_arg,  # pyright: ignore
            output_mode,
        )

        io.render(
            "target_contents.jinja2",
            {
                "backup_mode": backup_mode.value.title(),
                "source": str(source.path),
                "target": str(target.path),
                "existing_backup": target.existing_backup.name if target.existing_backup else None,
                "backup_name": target.backup_name,
                "target_content": target.content,
            },
        )

    @ex(
        help="Configure scarab",
        arguments=[
            (
                ["-p", "--put"],
                {
                    "help": "Create an example config-file at ~/.scarab.yml",
                    "action": "store_true",
                    "dest": "put",
                },
            ),
            (
                ["-f", "--force"],
                {
                    "help": "Override existing config file at ~/.scarab.yml",
                    "action": "store_true",
                    "dest": "force",
                },
            ),
        ],
    )  # pyright: ignore
    def config(self) -> None:
        put: bool = self.app.pargs.put  # pyright: ignore
        force: bool = self.app.pargs.force  # pyright: ignore

        if put:
            config.put_example(force)  # pyright: ignore
