import os
import shutil
from typing import Optional, Tuple

from cement import Controller, ex, get_version  # pyright: ignore

import app.config as config
import app.init as init
import app.io as io
from app.globals import (
    BackupMode,
    OutputMode,
    ScarabArgumentError,
    ScarabOptionError,
    ScarabProfile,
)
from app.locations import Source, Target
from app.records import BackupParams, NameFormats, TargetContent

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

            self.auto(profile)

    @ex(
        help="Automatically create and update backups",
        arguments=[
            *backup_controller_args,
            (
                ["-i", "--ignore-datetime"],
                {
                    "help": "Select the latest existing backup-directory and rename it",
                    "action": "store_true",
                    "dest": "ignore_datetime",
                },
            ),
        ],
    )  # pyright: ignore
    def auto(self, profile: Optional[ScarabProfile] = None) -> None:
        source_arg: str
        target_arg: str
        name_arg: int
        ignore_datetime: bool

        if profile:
            (
                source_arg,
                target_arg,
                name_arg,
                ignore_datetime,
            ) = self._init_required_args_from_config(profile)
        else:
            source_arg, target_arg, name_arg, ignore_datetime = self._init_required_args_from_cli()

        source: Source = init.init_location(Source(source_arg))
        target: Target = init.init_location(Target(target_arg))

        name_formats = NameFormats(source.path.name)
        target.backup_name = name_formats.select(name_arg)

        # target.select_existing_backup(ignore_datetime, name_arg, name_formats)

        if ignore_datetime:
            if name_arg <= 3:
                name_to_find: str = name_formats.select(1)
            else:
                name_to_find: str = name_formats.select(4)

            matches: list[str] = [
                dir
                for dir in sorted(target.content_dirs, reverse=True)
                if dir.startswith(name_to_find)
            ]
            target.existing_backup = target.path / matches[0] if matches else None

        else:
            if target.backup_name in target.content_dirs:
                target.existing_backup = target.path / target.backup_name

        if source.path == target.existing_backup:
            raise ScarabArgumentError(
                "Source is the selected existing backup-directory", "source", str(source.path)
            )

        self._execute(source, target, "Auto")

    @ex(
        help="Create a new backup",
        arguments=backup_controller_args,
    )  # pyright: ignore
    def create(self) -> None:
        source_arg: str
        target_arg: str
        name_arg: Optional[int]
        output_mode: OutputMode
        source_arg, target_arg, name_arg, output_mode = self._init_optional_args()

        source: Source = init.init_location_interactively(source_arg, Source, output_mode)
        target: Target = init.init_location_interactively(target_arg, Target, output_mode)

        if target.is_media_dir:
            target = init.select_media_dir(source, target, output_mode)

        io.render("target_contents.jinja2", TargetContent(target_content=target.content))

        target.backup_name = init.select_backup_name(
            source,
            target,
            name_arg,
            output_mode,
            is_create=True,
        )

        self._execute(source, target, "Create")

    @ex(
        help="Update an existing backup",
        arguments=backup_controller_args,
    )  # pyright: ignore
    def update(self) -> None:
        source_arg: str
        target_arg: str
        name_arg: Optional[int]
        output_mode: OutputMode
        source_arg, target_arg, name_arg, output_mode = self._init_optional_args()

        source: Source = init.init_location_interactively(source_arg, Source, output_mode)
        target: Target = init.init_location_interactively(target_arg, Target, output_mode)

        if target.is_media_dir:
            target = init.select_media_dir(source, target, output_mode)

        target.existing_backup = init.select_backup_directory(target, output_mode)

        if source.path == target.existing_backup:
            raise ScarabArgumentError(
                "Source is the selected existing backup-directory", "source", str(source.path)
            )

        target.backup_name = init.select_backup_name(
            source,
            target,
            name_arg,
            output_mode,
        )

        self._execute(source, target, "Update")

    def _init_optional_args(self) -> Tuple[str, str, Optional[int], OutputMode]:
        quiet: bool = self.app.quiet  # pyright: ignore
        source_arg: Optional[str] = self.app.pargs.source  # pyright: ignore
        target_arg: Optional[str] = self.app.pargs.target  # pyright: ignore
        name_arg: Optional[int] = (
            int(self.app.pargs.name) if self.app.pargs.name else None  # pyright: ignore
        )

        if quiet:
            output_mode = OutputMode.QUIET
        else:
            output_mode = OutputMode.NORMAL

        return (
            source_arg,
            target_arg,
            name_arg,
            output_mode,
        )  # pyright: ignore

    def _init_required_args_from_config(self, profile: ScarabProfile) -> Tuple[str, str, int, bool]:
        args: ScarabProfile = profile  # pyright: ignore

        try:
            source_arg: str = args["source"]  # pyright: ignore
            target_arg: str = args["target"]  # pyright: ignore
            name_arg: str = args["name"]  # pyright: ignore
        except KeyError as e:
            raise ScarabOptionError(
                f"Your config-file is missing a required option", f"{e.args[0]}"
            )

        try:
            ignore_datetime: bool = args["ignore_datetime"]  # pyright: ignore
        except KeyError:
            ignore_datetime = False

        return (
            source_arg,
            target_arg,
            int(name_arg),
            ignore_datetime,
        )

    def _init_required_args_from_cli(self) -> Tuple[str, str, int, bool]:
        args: ScarabProfile = vars(self.app.pargs)  # pyright: ignore

        required_args: list[str] = ["source", "target", "name"]
        none_args: list[str] = [
            key
            for key, value in args.items()  # pyright: ignore
            if key in required_args and value is None
        ]
        if len(none_args) > 0:
            raise ScarabOptionError(f"You did not specify a required option", f"{none_args[0]}")
        else:
            source_arg: str = args["source"]  # pyright: ignore
            target_arg: str = args["target"]  # pyright: ignore
            name_arg: str = args["name"]  # pyright: ignore

            ignore_datetime: bool = args["ignore_datetime"]  # pyright: ignore

        return (
            source_arg,
            target_arg,
            int(name_arg),
            ignore_datetime,
        )

    def _execute(self, source: Source, target: Target, backup_mode: BackupMode) -> None:
        io.render(
            "backup_params.jinja2",
            BackupParams(
                backup_mode=backup_mode,
                source=source.path,
                target=target.path,
                existing_backup=target.existing_backup,
                backup_name=target.backup_name,
            ),
        )

        assert target.backup_name

        if target.existing_backup:
            shutil.rmtree(target.existing_backup)
        shutil.copytree(
            source.path, target.path / target.backup_name, ignore_dangling_symlinks=True
        )


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
