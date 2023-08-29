import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, call

import pytest
from pytest_mock import MockerFixture

import app.interactions as interactions
from app.globals import ScarabOptionError
from app.locations import Destination, Location, Source
from app.main import ScarabTest
from tests.conftest import get_content_with_slashed_dirs


def it_prints_sourcepath_and_destpath_with_sorted_dest_dir_top_level(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    valid_path: str = str(tmp_path)
    dir1: Path = tmp_path / "directory_1"
    dir1.mkdir()
    dir2: Path = tmp_path / "directory_2"
    dir2.mkdir()
    file: Path = tmp_path / "file.txt"
    file.touch()
    mock_render: Mock = mocker.patch("app.io.render")

    with ScarabTest(argv=["backup", "--source", valid_path, "--dest", valid_path]) as app:
        app.run()

        mock_render.assert_called_with(
            "dest_contents.jinja2",
            {
                "source": valid_path,
                "destination": valid_path,
                "destination_content": ["directory_1/", "directory_2/", "file.txt"],
            },
        )


def it_has_dir_selection_menu_with_rescan_option_when_in_media_dir(
    mocker: MockerFixture,
    media_dir_fixture: Path,
) -> None:
    dest_content: list[str] = [
        *sorted(get_content_with_slashed_dirs(media_dir_fixture)),
        "-> Rescan Directory",
    ]
    dest_content_rescan_option_num: int = len(dest_content)

    mock_render: Mock = mocker.patch("app.io.render")
    mock_input: Mock = mocker.patch("builtins.input")
    mock_input.side_effect = [dest_content_rescan_option_num, 1]

    destination: Location = interactions.select_media_dir(
        Source("~"), Destination(str(media_dir_fixture))
    )

    assert destination.path == media_dir_fixture / "directory_1"

    mock_render.assert_has_calls(
        [
            call(
                "select_directory.jinja2",
                {
                    "source": os.environ["HOME"],
                    "destination": str(media_dir_fixture),
                    "destination_content": dest_content,
                },
            ),
            call(
                "select_directory.jinja2",
                {
                    "source": os.environ["HOME"],
                    "destination": str(media_dir_fixture),
                    "destination_content": dest_content,
                },
            ),
        ]
    )

    mock_input.assert_called_with("Number: ")
    assert mock_input.call_count == 2


@pytest.mark.parametrize(
    "path_in",
    [os.environ["HOME"], "~", "$HOME"],
)
def it_expands_and_validates_paths(
    path_in: str | None,
) -> None:
    source: Location = interactions.check_path(Source(path_in))

    assert str(source.path) == os.environ["HOME"]


def it_normalizes_dot_paths() -> None:
    source: Location = interactions.check_path(Source("."))

    assert source.path == Path(".").resolve()


@pytest.mark.parametrize(
    "path_in",
    [
        None,
        "/invalid",
    ],
)
def it_gets_paths_from_input_when_arg_is_invalid_or_missing(
    mocker: MockerFixture,
    path_in: str | None,
) -> None:
    correct_path: str = os.environ["HOME"]
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.side_effect = ["", "invalid_again", correct_path]

    source: Location = interactions.check_path(Source(path_in))

    mock_input.assert_called_with("Path: ")
    assert mock_input.call_count == 3
    assert str(source.path) == correct_path


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
