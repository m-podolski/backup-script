import datetime
import os
import socket
from pathlib import Path
from unittest.mock import MagicMock, Mock, _Call, call  # pyright: ignore

import pytest
from pytest_mock import MockerFixture

import app.interactions as interactions
from app.globals import BackupMode, ScarabArgumentError, ScarabOptionError
from app.locations import Location, Source, Target
from app.main import ScarabTest
from tests.conftest import create_files_and_dirs, get_content_with_slashed_dirs


@pytest.mark.parametrize(
    "path_in",
    [os.environ["HOME"], "~", "$HOME"],
)
def it_expands_paths(
    path_in: str | None,
) -> None:
    source: Source = interactions.init_location(path_in, Source)

    assert str(source.path) == os.environ["HOME"]


def it_normalizes_relative_paths(tmp_path: Path) -> None:
    create_files_and_dirs(tmp_path, ["dir/"])
    os.chdir(tmp_path)
    source1: Source = Source(".")
    source2: Source = Source("./dir")

    assert str(source1.path) == str(Path(".").resolve())
    assert str(source2.path) == str(Path("./dir").resolve())


@pytest.mark.parametrize(
    "path_in",
    [
        None,
        "/invalid",
    ],
)
def it_gets_paths_if_arg_is_missing_empty_or_invalid(
    mocker: MockerFixture,
    path_in: str | None,
) -> None:
    valid_path: str = os.environ["HOME"]
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.side_effect = ["", "invalid_again", valid_path]

    source: Source = interactions.init_location(path_in, Source)

    mock_input.assert_called_with("Path: ")
    assert mock_input.call_count == 3
    assert str(source.path) == valid_path


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


def it_raises_when_source_is_the_selected_existing_backup_dir(
    mocker: MockerFixture, tmp_path: Path
) -> None:
    create_files_and_dirs(tmp_path, ["dir_2023-09-04/"])
    test_path: Path = tmp_path / "dir_2023-09-04"
    mock_input: Mock = mocker.patch("builtins.input")
    mock_input.return_value = "1"

    with pytest.raises(
        ScarabArgumentError,
        match=f"Scarab got invalid or conflicting arguments: Source is the selected existing backup-directory\n'source' is '{str(test_path)}'",
    ):
        with ScarabTest(
            argv=[
                "backup",
                "--source",
                str(test_path),
                "--target",
                str(tmp_path),
                "--update",
                "--name",
                "1",
            ]
        ) as app:
            app.run()


def it_selects_dirs_called_backup_if_present_in_target(tmp_path: Path) -> None:
    create_files_and_dirs(
        tmp_path, ["Backup/", "Backups/", "backup/", "Backsnup/", "other/", "Backup.txt"]
    )

    target: Location = Target(tmp_path)

    assert str(target.path) == str(tmp_path / "Backup")


def it_gets_dir_selection_with_rescan_option_when_in_media_dir(
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

    target: Target = interactions.select_media_dir(Source("~"), Target(media_dir_fixture))

    call_list_item: _Call = call(
        "select_directory.jinja2",
        {
            "source": os.environ["HOME"],
            "target": str(media_dir_fixture),
            "target_content": target_content,
        },
    )

    mock_input.assert_called_with("Number: ")
    mock_render.assert_has_calls(
        [
            call_list_item,
            call_list_item,
        ]
    )
    assert mock_input.call_count == 2
    assert str(target.path) == str(media_dir_fixture / "directory_1")


def it_gets_backup_mode_if_not_given(mocker: MockerFixture) -> None:
    mock_render: Mock = mocker.patch("app.io.render")
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.return_value = "2"

    mode: BackupMode = interactions.select_backup_mode()

    mock_input.assert_called_with("Number: ")
    mock_render.assert_called_with(
        "select_backup_mode.jinja2",
        {
            "modes": ["Create New", "Update Existing"],
        },
    )
    assert mode == BackupMode.UPDATE


def it_gets_dir_at_target_when_in_update_mode(mocker: MockerFixture, tmp_path: Path) -> None:
    create_files_and_dirs(tmp_path, [".file_at_the_top", "backup_1/", "backup_2/", "file_2.txt"])
    create_files_and_dirs(tmp_path / "backup_2", ["dir_1/", "dir_2/"])

    mock_render: Mock = mocker.patch("app.io.render")
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.return_value = "2"

    with ScarabTest(
        argv=["backup", "--source", "/tmp", "--target", str(tmp_path), "--update", "--name", "1"]
    ) as app:
        app.run()

        mock_input.assert_called_with("Number: ")

        assert mock_render.mock_calls[0].args[0] == "select_target_directory.jinja2"
        assert mock_render.mock_calls[0].args[1]["target_content"] == ["backup_1", "backup_2"]

        assert mock_render.mock_calls[1].args[0] == "target_contents.jinja2"
        assert mock_render.mock_calls[1].args[1]["target"] == str(tmp_path)
        assert mock_render.mock_calls[1].args[1]["existing_backup"] == "backup_2"
        assert mock_render.mock_calls[1].args[1]["target_content"] == ["dir_1/", "dir_2/"]


def it_gets_the_target_name_from_a_selection_menu(mocker: MockerFixture, tmp_path: Path) -> None:
    create_files_and_dirs(tmp_path, ["test/"])
    test_source_path: Path = tmp_path / "test"
    mock_render: Mock = mocker.patch("app.io.render")
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.return_value = "5"

    target_name: str = interactions.select_backup_name(
        Source(test_source_path), Target("~"), BackupMode.UPDATE
    )

    mock_input.assert_called_with("Number: ")
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
    assert target_name == _make_backup_name("test")


def it_gets_the_target_name_again_in_create_mode_if_it_already_exists(
    mocker: MockerFixture, tmp_path: Path
) -> None:
    create_files_and_dirs(tmp_path, ["target/"])
    test_target_path: Path = tmp_path / "target"
    create_files_and_dirs(test_target_path, ["directory/"])
    test_target_sub_path: Path = test_target_path / "directory"

    mock_render: Mock = mocker.patch("app.io.render")
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.side_effect = ["1", "5"]

    target_name: str = interactions.select_backup_name(
        Source(test_target_sub_path), Target(test_target_path), BackupMode.CREATE
    )

    call_list_item: _Call = call(
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

    mock_render.assert_has_calls(
        [
            call_list_item,
            call_list_item,
        ]
    )
    assert target_name == _make_backup_name("directory")


def it_prints_backup_information(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    create_files_and_dirs(tmp_path, ["existing_1/", "existing_2/", "file.txt"])
    source_path: Path = Path(f"/home/{os.environ['USER']}")

    mock_render: Mock = mocker.patch("app.io.render")
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.return_value = "5"

    with ScarabTest(
        argv=["backup", "--source", str(source_path), "--target", str(tmp_path), "--create"]
    ) as app:
        app.run()

        mock_render.assert_has_calls(
            [
                call(
                    "target_contents.jinja2",
                    {
                        "backup_mode": "Create",
                        "source": str(source_path),
                        "target": str(tmp_path),
                        "existing_backup": None,
                        "backup_name": _make_backup_name(source_path.name),
                        "target_content": ["existing_1/", "existing_2/", "file.txt"],
                    },
                ),
            ]
        )


def _make_backup_name(path_name: str) -> str:
    user: str = os.environ["USER"]
    host: str = socket.gethostname()
    date_time: str = datetime.datetime.today().strftime("%Y-%m-%d")
    return f"{user}@{host}_{path_name}_{date_time}"
