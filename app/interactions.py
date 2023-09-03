import datetime
import os
import socket
from pathlib import Path
from typing import Optional

import app.io as appio
from app.globals import BackupMode, OutputMode
from app.locations import Source, Target


def check_path(
    location: Source | Target, output_mode: OutputMode = OutputMode.NORMAL
) -> Source | Target:
    if location.path_is_initialized:
        if location.exists:
            return location
        else:
            location.path = appio.get_path_input(
                location.location_messages["INVALID"],
                output_mode,
            )
            return check_path(location, output_mode)
    else:
        location.path = appio.get_path_input(location.messages["NO_PATH_GIVEN"], output_mode)
        return check_path(location, output_mode)


def select_media_dir(
    source: Source, target: Target, output_mode: OutputMode = OutputMode.NORMAL
) -> Target:
    appio.render(
        "select_directory.jinja2",
        {
            "source": str(source.path),
            "target": str(target.path),
            "target_content": [*target.content, "-> Rescan Directory"],
        },
    )
    selected_option: int = int(appio.get_input("Number: ", output_mode))
    selected_option_is_rescan: bool = selected_option == len(target.content) + 1

    if selected_option_is_rescan:
        return select_media_dir(source, target, output_mode)
    else:
        selected_dir: str = target.content[selected_option - 1]
        target.path = target.path / selected_dir
        return target


def select_backup_mode(output_mode: OutputMode = OutputMode.NORMAL) -> BackupMode:
    appio.render(
        "select_backup_mode.jinja2",
        {
            "modes": ["Create New", "Update Existing"],
        },
    )
    selected_option: int = int(appio.get_input("Number: ", output_mode))
    return [mode for mode in BackupMode][selected_option - 1]


# def select_target_directory(target: Location, output_mode: OutputMode = OutputMode.NORMAL) -> Path:
def select_backup_directory(target: Target, output_mode: OutputMode = OutputMode.NORMAL) -> Path:
    appio.render(
        "select_target_directory.jinja2",
        {
            "target_content": target.content_dirs,
        },
    )
    selected_option: int = int(appio.get_input("Number: ", output_mode))
    selected_dir: str = target.content_dirs[selected_option - 1]
    return target.path / selected_dir


def select_backup_name(
    source_dir: str,
    target: Target,
    backup_mode: BackupMode,
    name_arg: Optional[str] = None,
    output_mode: OutputMode = OutputMode.NORMAL,
) -> str:
    user: str = os.environ["USER"]
    host: str = socket.gethostname()
    date: str = datetime.datetime.today().strftime("%Y-%m-%d")
    time: str = datetime.datetime.today().strftime("%H-%M-%S")

    name_formats: dict[str, str] = {
        "<source-dir>": source_dir,
        "<source-dir>_<date>": f"{source_dir}_{date}",
        "<source-dir>_<date-time>": f"{source_dir}_{date}-{time}",
        "<user>@<host>_<source-dir>": f"{user}@{host}_{source_dir}",
        "<user>@<host>_<source-dir>_<date>": f"{user}@{host}_{source_dir}_{date}",
        "<user>@<host>_<source-dir>_<date-time>": f"{user}@{host}_{source_dir}_{date}-{time}",
    }

    if name_arg is None:
        appio.render(
            "select_target_name.jinja2",
            {
                "name_formats": [format for format in name_formats.keys()],
            },
        )
        selected_option: int = int(appio.get_input("Number: ", output_mode))
    else:
        selected_option: int = int(name_arg)

    selected_format: str = list(name_formats.values())[selected_option - 1]
    selected_name_already_exists: bool = selected_format in [
        item[0 : len(item) - 1 :] for item in target.content
    ]

    if backup_mode is BackupMode.CREATE and selected_name_already_exists:
        return select_backup_name(source_dir, target, backup_mode, name_arg, output_mode)

    return selected_format
