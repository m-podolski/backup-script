import os
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from pytest_mock import MockerFixture

import app.locations as locations
from app.exceptions import ScarabOptionError
from app.locations import Location, Source
from app.main import ScarabTest
from tests.conftest import replace_homedir_with_test_parameter


def it_prints_the_sourcepath_and_the_destpath_dir_top_level(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    valid_path: str = str(tmp_path)
    dir: Path = tmp_path / "directory"
    dir.mkdir()
    file: Path = tmp_path / "file.txt"
    file.touch()
    mock_render: Mock = mocker.patch("app.io.render")

    with ScarabTest(argv=["backup", "--source", valid_path, "--dest", valid_path]) as app:
        app.run()

        mock_render.assert_called_with(
            "backup.jinja2",
            {
                "source": valid_path,
                "destination": valid_path,
                "destination_content": ["directory/", "file.txt"],
            },
        )


def it_uses_the_media_dir_when_set_and_ignores_dest_args(mocker: MockerFixture) -> None:
    mock_render: Mock = mocker.patch("app.io.render")
    media_dir: str = f"/media/{os.environ['USER']}"

    def add_slash_to_dir(path: Path) -> str:
        if path.is_dir():
            return f"{path.name}/"
        else:
            return path.name

    dest_content_with_slashed_dirs: list[str] = [
        add_slash_to_dir(path) for path in Path(f"/media/{os.environ['USER']}").iterdir()
    ]

    with ScarabTest(argv=["backup", "--source", "~", "--dest", "~", "--media"]) as app:
        app.run()

        mock_render.assert_called_with(
            "backup.jinja2",
            {
                "source": os.environ["HOME"],
                "destination": media_dir,
                "destination_content": dest_content_with_slashed_dirs,
            },
        )


@pytest.mark.parametrize(
    "path_in",
    [
        os.environ["HOME"],
        "~",
        "$HOME",
    ],
)
def it_expands_and_validates_paths(
    tmp_path: Path,
    path_in: str | None,
) -> None:
    path_in = f"{replace_homedir_with_test_parameter(tmp_path, path_in)}"
    correct_path: str = str(tmp_path)

    source: Location = locations.check_path(Source(path_in))

    assert str(source.path) == correct_path


@pytest.mark.parametrize(
    "path_in",
    [
        None,
        "/invalid",
    ],
)
def it_gets_paths_from_input_when_arg_is_invalid_or_missing(
    mocker: MockerFixture,
    tmp_path: Path,
    path_in: str | None,
) -> None:
    correct_path: str = str(tmp_path)
    mock_input: MagicMock = mocker.patch("builtins.input")
    mock_input.side_effect = ["", "invalid_again", correct_path]

    source: Location = locations.check_path(Source(path_in))

    mock_input.assert_called_with("Path: ")
    assert mock_input.call_count == 3
    assert str(source.path) == correct_path


def it_raises_in_quiet_mode_when_input_required(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    mocker.patch("builtins.input")

    with pytest.raises(
        ScarabOptionError,
        match=r"^Scarab got wrong or conflicting arguments: Cannot receive input in quiet mode",
    ):
        with ScarabTest(argv=["-q", "backup", "--source", "invalid"]) as app:
            app.run()
