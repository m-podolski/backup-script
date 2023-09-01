import datetime
import os
import socket
from pathlib import Path
from unittest.mock import MagicMock, Mock, call

import pytest
from pytest_mock import MockerFixture

import app.interactions as interactions
from app.globals import BackupMode, OutputMode, ScarabOptionError
from app.locations import Location, Source, Target
from app.main import ScarabTest
from tests.conftest import create_files_and_dirs, get_content_with_slashed_dirs


@pytest.mark.parametrize(
    "path_in",
    [os.environ["HOME"], "~", "$HOME"],
)
def it_expands_and_validates_paths(
    path_in: str | None,
) -> None:
    source: Location = interactions.check_path(Source(path_in), OutputMode.NORMAL)

    assert str(source.path) == os.environ["HOME"]


def it_normalizes_relative_paths() -> None:
    source1: Location = Source(".")
    source2: Location = Source("./test")

    assert str(source1.path) == str(Path(".").resolve())
    assert str(source2.path) == str(Path("./test").resolve())


@pytest.mark.parametrize(
    "path_in",
    [
        None,
        "/invalid",
    ],
)
def it_gets_paths_if_arg_is_invalid_or_missing(
    mocker: MockerFixture,
    path_in: str | None,
) -> None:
    valid_path: str = os.environ["HOME"]
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.side_effect = ["", "invalid_again", valid_path]

    source: Location = interactions.check_path(Source(path_in), OutputMode.NORMAL)

    mock_input.assert_called_with("Path: ")
    assert mock_input.call_count == 3
    assert str(source.path) == valid_path


def it_raises_when_source_and_target_paths_are_identical(mocker: MockerFixture) -> None:
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.return_value = "1"

    with pytest.raises(
        ScarabOptionError,
        match=r": Source and target are identical$",
    ):
        with ScarabTest(argv=["backup", "--source", "~", "--target", "~"]) as app:
            app.run()


def it_raises_in_quiet_mode_when_input_required(
    mocker: MockerFixture,
) -> None:
    mocker.patch("builtins.input")

    with pytest.raises(
        ScarabOptionError,
        match=r": Cannot receive input in quiet mode$",
    ):
        with ScarabTest(argv=["-q", "backup", "--source", "invalid"]) as app:
            app.run()


def it_selects_dirs_called_backup_if_present_in_target(tmp_path: Path) -> None:
    create_files_and_dirs(
        tmp_path, ["Backup/", "Backups/", "backup/", "Backsnup/", "other/", "Backup.txt"]
    )

    target: Location = Target(tmp_path)

    assert str(target.path) == str(tmp_path / "Backup")


def it_gets_existing_selection_with_rescan_option_when_in_media_dir(
    mocker: MockerFixture,
    media_dir_fixture: Path,
) -> None:
    create_files_and_dirs(media_dir_fixture, ["directory_1/", "directory_2/"])
    target_content: list[str] = [
        *sorted(get_content_with_slashed_dirs(media_dir_fixture)),
        "-> Rescan Directory",
    ]
    target_content_rescan_option_num: int = len(target_content)

    mock_render: Mock = mocker.patch("app.io.render")
    mock_input: Mock = mocker.patch("builtins.input")
    mock_input.side_effect = [target_content_rescan_option_num, "1"]

    target: Location = interactions.select_media_dir(
        Source("~"), Target(str(media_dir_fixture)), OutputMode.NORMAL
    )

    assert str(target.path) == str(media_dir_fixture / "directory_1")
    mock_render.assert_has_calls(
        [
            call(
                "select_directory.jinja2",
                {
                    "source": os.environ["HOME"],
                    "target": str(media_dir_fixture),
                    "target_content": target_content,
                },
            ),
            call(
                "select_directory.jinja2",
                {
                    "source": os.environ["HOME"],
                    "target": str(media_dir_fixture),
                    "target_content": target_content,
                },
            ),
        ]
    )
    mock_input.assert_called_with("Number: ")
    assert mock_input.call_count == 2


def it_gets_backup_mode_if_not_given(mocker: MockerFixture) -> None:
    mock_render: Mock = mocker.patch("app.io.render")
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.return_value = "2"

    mode: BackupMode = interactions.select_backup_mode(OutputMode.NORMAL)

    assert mode == BackupMode.UPDATE
    mock_render.assert_called_with(
        "select_backup_mode.jinja2",
        {
            "modes": ["Create New", "Update Existing"],
        },
    )
    mock_input.assert_called_with("Number: ")


def it_gets_dir_at_target_when_in_update_mode(mocker: MockerFixture, tmp_path: Path) -> None:
    create_files_and_dirs(tmp_path, ["backup_1/", "backup_2/", "file.txt"])
    test_path: Path = tmp_path / "backup_2"
    create_files_and_dirs(test_path, ["dir_1/", "dir_2/"])

    mock_render: Mock = mocker.patch("app.io.render")
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.side_effect = ["2", "1"]  # second is the target-name-selection

    with ScarabTest(
        argv=["backup", "--source", "/tmp", "--target", str(tmp_path), "--update"]
    ) as app:
        app.run()

        mock_render.assert_has_calls(
            [
                call(
                    "select_target_directory.jinja2",
                    {
                        "target_content": ["backup_1/", "backup_2/"],
                    },
                ),
                call(
                    "select_target_name.jinja2",
                    {
                        "name_formats": [
                            "<source-dir>",
                            "<source-dir>_<date>",
                            "<source-dir>_<date-time>",
                            "<user>@<host>_<source-dir>",
                            "<user>@<host>_<source-dir>_<date>",
                            "<user>@<host>_<source-dir>_<date-time>",
                        ],
                    },
                ),
                call(
                    "target_contents.jinja2",
                    {
                        "source": "/tmp",
                        "target": str(test_path),
                        "backup_mode": "Update",
                        "target_name": "tmp",
                        "target_content": ["dir_1/", "dir_2/"],
                    },
                ),
            ]
        )
        mock_input.assert_called_with("Number: ")


def it_gets_the_target_name_from_a_selection_menu(mocker: MockerFixture, tmp_path: Path) -> None:
    create_files_and_dirs(tmp_path, ["test/"])
    test_path: Path = tmp_path / "test"
    mock_render: Mock = mocker.patch("app.io.render")
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.return_value = "6"

    target_name: str = interactions.select_target_name(test_path.name, OutputMode.NORMAL)

    assert target_name == _make_target_name("test")

    mock_render.assert_called_with(
        "select_target_name.jinja2",
        {
            "name_formats": [
                "<source-dir>",
                "<source-dir>_<date>",
                "<source-dir>_<date-time>",
                "<user>@<host>_<source-dir>",
                "<user>@<host>_<source-dir>_<date>",
                "<user>@<host>_<source-dir>_<date-time>",
            ],
        },
    )
    mock_input.assert_called_with("Number: ")


def it_prints_backup_information(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    create_files_and_dirs(tmp_path, ["existing_1/", "existing_2/", "file.txt"])
    source_path: Path = Path(f"/home/{os.environ['USER']}")

    mock_render: Mock = mocker.patch("app.io.render")
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.return_value = "6"

    with ScarabTest(
        argv=["backup", "--source", str(source_path), "--target", str(tmp_path), "--create"]
    ) as app:
        app.run()

        mock_render.assert_has_calls(
            [
                call(
                    "target_contents.jinja2",
                    {
                        "source": str(source_path),
                        "target": str(tmp_path),
                        "backup_mode": "Create",
                        "target_name": _make_target_name(source_path.name),
                        "target_content": ["existing_1/", "existing_2/", "file.txt"],
                    },
                ),
            ]
        )


def _make_target_name(path_name: str) -> str:
    user: str = os.environ["USER"]
    host: str = socket.gethostname()
    date_time: str = datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    return f"{user}@{host}_{path_name}_{date_time}"
