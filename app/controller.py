import os
from typing import Optional, Tuple

from cement import Controller, ex, get_version  # pyright: ignore

import app.config as config
import app.interactions as interactions
import app.io as io
from app.globals import OutputMode, ScarabArgumentError, ScarabProfile
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


backup_controller_args: list[tuple[list[str], dict[str, str]]] = [
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
]


class Backup(Controller):
    class Meta:  # pyright: ignore
        label: str = "backup"
        stacked_on: str = "base"
        stacked_type: str = "nested"
        description: str = "Back up from from a sourcepath to a targetpath"

    @ex(
        help="Use a profile from your config-file",
        arguments=[
            (
                ["profile_name"],
                {
                    "help": "Use a profile from your config-file",
                },
            ),
        ],
    )  # pyright: ignore
    def profile(self) -> None:
        profile_arg: Optional[str] = self.app.pargs.profile_name  # pyright: ignore

        if profile_arg is not None:
            profiles: list[ScarabProfile] = self.app.config.get(  # pyright: ignore
                "scarab", "profiles"
            )

            def find_profile(profile: ScarabProfile) -> bool:
                return profile["profile"] == profile_arg  # pyright: ignore

            profile: ScarabProfile = list(filter(find_profile, profiles))[0]  # pyright: ignore

            match profile["mode"]:
                case "create":
                    self.create(profile)
                case "update":
                    self.update(profile)
                case _:
                    pass

    @ex(
        help="Create a new backup",
        arguments=backup_controller_args,
    )  # pyright: ignore
    def create(self, profile: Optional[ScarabProfile] = None) -> None:
        source: Source
        target: Target
        name_arg: Optional[str]
        output_mode: OutputMode

        source, target, name_arg, output_mode = self._initialize(profile)

        if target.is_media_dir:
            target = interactions.select_media_dir(source, target, output_mode)

        io.render(
            "target_contents.jinja2",
            {
                "target_content": target.content,
            },
        )

        target.backup_name = interactions.select_backup_name(
            source,
            target,
            name_arg,  # pyright: ignore
            output_mode,
            is_create=True,
        )

        io.render(
            "backup_params.jinja2",
            {
                "backup_mode": "Create",
                "source": str(source.path),
                "target": str(target.path),
                "existing_backup": target.existing_backup.name if target.existing_backup else None,
                "backup_name": target.backup_name,
            },
        )

    @ex(
        help="Update an existing backup",
        arguments=backup_controller_args,
    )  # pyright: ignore
    def update(self, profile: Optional[ScarabProfile] = None) -> None:
        source: Source
        target: Target
        name_arg: Optional[str]
        output_mode: OutputMode

        source, target, name_arg, output_mode = self._initialize(profile)

        if target.is_media_dir:
            target = interactions.select_media_dir(source, target, output_mode)

        target.existing_backup = interactions.select_backup_directory(target, output_mode)

        if source.path == target.existing_backup:
            raise ScarabArgumentError(
                "Source is the selected existing backup-directory", "source", str(source.path)
            )

        target.backup_name = interactions.select_backup_name(
            source,
            target,
            name_arg,  # pyright: ignore
            output_mode,
        )

        io.render(
            "backup_params.jinja2",
            {
                "backup_mode": "Update",
                "source": str(source.path),
                "target": str(target.path),
                "existing_backup": target.existing_backup.name if target.existing_backup else None,
                "backup_name": target.backup_name,
            },
        )

    def _initialize(
        self, profile: Optional[ScarabProfile] = None
    ) -> Tuple[Source, Target, Optional[str], OutputMode]:
        quiet: bool = self.app.quiet  # pyright: ignore
        source_arg: Optional[str] = (
            self.app.pargs.source if profile is None else profile["source"]  # pyright: ignore
        )
        target_arg: Optional[str] = (
            self.app.pargs.target if profile is None else profile["target"]  # pyright: ignore
        )
        name_arg: Optional[str] = (
            self.app.pargs.name if profile is None else profile["name"]  # pyright: ignore
        )

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

        return source, target, name_arg, output_mode  # pyright: ignore[reportUnknownVariableType]


class Config(Controller):
    class Meta:  # pyright: ignore
        label: str = "config"
        stacked_on: str = "base"
        stacked_type: str = "nested"

    @ex(
        help="Create an example config-file at ~/.scarab.yml",
        arguments=[
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
    def put(self) -> None:
        force: bool = self.app.pargs.force  # pyright: ignore

        config.put_example(force)  # pyright: ignore
