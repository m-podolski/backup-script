import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, call

import pytest
from pytest_mock import MockerFixture

import app.interactions as interactions
from app.globals import OutputMode, ScarabOptionError
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


def it_normalizes_dot_paths() -> None:
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
def it_gets_paths_from_input_if_arg_is_invalid_or_missing(
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


def it_raises_in_quiet_mode_when_input_required(
    mocker: MockerFixture,
) -> None:
    mocker.patch("builtins.input")

    with pytest.raises(
        ScarabOptionError,
        match=r"^Scarab got wrong or conflicting arguments: Cannot receive input in quiet mode",
    ):
        with ScarabTest(argv=["-q", "backup", "--source", "invalid"]) as app:
            app.run()


def it_prints_sourcepath_and_targetpath_with_sorted_target_dir_top_level(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    valid_path: str = str(tmp_path)
    create_files_and_dirs(tmp_path, ["directory_1/", "directory_2/", "file.txt"])
    mock_render: Mock = mocker.patch("app.io.render")

    with ScarabTest(argv=["backup", "--source", valid_path, "--target", valid_path]) as app:
        app.run()

        mock_render.assert_called_with(
            "target_contents.jinja2",
            {
                "source": valid_path,
                "target": valid_path,
                "target_content": ["directory_1/", "directory_2/", "file.txt"],
            },
        )


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


def it_selects_dirs_called_backup_if_present_in_target(tmp_path: Path) -> None:
    create_files_and_dirs(
        tmp_path, ["Backup/", "Backups/", "backup/", "Backsnup/", "other/", "Backup.txt"]
    )

    target: Location = Target(tmp_path)

    assert str(target.path) == str(tmp_path / "Backup")
