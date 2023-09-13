import datetime
import os
import socket
from pathlib import Path
from typing import Literal, Optional, TypeAlias, TypeVar

import app.io as io
from app.globals import (
    NameFormats,
    OutputMode,
    ScarabArgumentError,
    ScarabMessage,
    TargetContent,
)
from app.locations import Source, Target

T = TypeVar("T", Source, Target)


def init_location(
    path_arg: Optional[str],
    location: type[T],
    output_mode: OutputMode = OutputMode.NORMAL,
) -> T:
    path_input: str = _check_for_empty_arg(path_arg, location.__name__, output_mode)
    return _check_path(location(path_input), output_mode)


def _check_for_empty_arg(path_arg: Optional[str], name: str, output_mode: OutputMode) -> str:
    if path_arg is None or path_arg == "":
        arg: str = io.get_path_input(_get_message("NO_PATH_GIVEN", name), output_mode)
        return _check_for_empty_arg(arg, name, output_mode)
    else:
        return path_arg


def _check_path(location: T, output_mode: OutputMode = OutputMode.NORMAL) -> T:
    if location.is_valid:
        return location
    else:
        if output_mode is OutputMode.AUTO:
            raise ScarabArgumentError(
                "A location has an invalid path",
                f"{location.name.lower()}",
                f"{str(location.path)}",
            )
        location.path = io.get_path_input(
            _get_message("INVALID_PATH", location.name),
            output_mode,
        )
        return _check_path(location, output_mode)


MessageType: TypeAlias = Literal["INVALID_PATH", "NO_PATH_GIVEN"]


def _get_message(key: MessageType, name: str) -> ScarabMessage:
    messages: dict[MessageType, ScarabMessage] = {
        "INVALID_PATH": ScarabMessage(
            f"Your {name.lower()} is not a valid directory! Please check and enter it again."
        ),
        "NO_PATH_GIVEN": ScarabMessage(
            f"Please specify a {name}-path to the directory you want {'backed up' if name == 'source' else 'to back up to'}."
        ),
    }
    return messages[key]


def select_media_dir(
    source: Source, target: Target, output_mode: OutputMode = OutputMode.NORMAL
) -> Target:
    io.render(
        "select_directory.jinja2",
        TargetContent(
            source=source.path,
            target=target.path,
            target_content=[*target.content, "-> Rescan Directory"],
        ),
    )
    selected_option: int = int(io.get_input("Number: ", output_mode))
    selected_option_is_rescan: bool = selected_option == len(target.content) + 1

    if selected_option_is_rescan:
        return select_media_dir(source, target, output_mode)
    else:
        selected_dir: str = target.content[selected_option - 1]
        target.path = target.path / selected_dir
        return target


def select_backup_directory(target: Target, output_mode: OutputMode = OutputMode.NORMAL) -> Path:
    io.render(
        "select_target_directory.jinja2",
        TargetContent(
            target_content=target.content_dirs,
        ),
    )
    selected_option: int = int(io.get_input("Number: ", output_mode))
    selected_dir: str = target.content_dirs[selected_option - 1]
    return target.path / selected_dir


def select_backup_name(
    source: Source,
    target: Target,
    name_arg: Optional[int] = None,
    output_mode: OutputMode = OutputMode.NORMAL,
    is_create: bool = False,
) -> str:
    user: str = os.environ["USER"]
    host: str = socket.gethostname()
    date: str = datetime.datetime.today().strftime("%Y-%m-%d")
    time: str = datetime.datetime.today().strftime("%H-%M-%S")

    name_formats: dict[str, str] = {
        "<source-dir>": source.path.name,
        "<source-dir>_<date>": f"{source.path.name}_{date}",
        "<source-dir>_<date-time>": f"{source.path.name}_{date}-{time}",
        "<user>@<host>_<source-dir>": f"{user}@{host}_{source.path.name}",
        "<user>@<host>_<source-dir>_<date>": f"{user}@{host}_{source.path.name}_{date}",
        "<user>@<host>_<source-dir>_<date-time>": f"{user}@{host}_{source.path.name}_{date}-{time}",
    }

    if name_arg is None:
        io.render(
            "select_target_name.jinja2",
            {
                "name_formats": [format for format in name_formats.keys()],
            },
        )
        selected_option: int = int(io.get_input("Number: ", output_mode))
    else:
        selected_option = name_arg

    selected_format: str = list(name_formats.values())[selected_option - 1]
    selected_name_already_exists: bool = selected_format in [
        item[0 : len(item) - 1 :] for item in target.content
    ]

    if is_create and selected_name_already_exists:
        return select_backup_name(source, target, name_arg, output_mode, is_create)

    return selected_format
