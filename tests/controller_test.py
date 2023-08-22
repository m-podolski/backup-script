from pathlib import Path
from unittest.mock import Mock
import pytest
from pytest_mock import MockerFixture
from app.exceptions import ScarabOptionError

from app.main import ScarabTest
from tests.conftest import HOME_DIR, replace_homedir_with_test_parameter


@pytest.mark.parametrize(
    "path_in",
    [
        (f"{HOME_DIR}"),
        ("~"),
        ("$HOME"),
    ],
)
def it_expands_and_validates_paths(
    mocker: MockerFixture,
    tmp_path: Path,
    path_in: str | None,
) -> None:
    path_in = f"{replace_homedir_with_test_parameter(tmp_path, path_in)}"
    correct_path: str = str(tmp_path.absolute())
    mock_print: Mock = mocker.patch("builtins.print")

    with ScarabTest(argv=["backup", "--source", path_in, "--dest", path_in]) as app:
        app.run()

        mock_print.assert_called_with(
            {"source": Path(correct_path).absolute(), "dest": Path(correct_path).absolute()}
        )


@pytest.mark.parametrize(
    "path_in",
    [
        (None),
        (f"{HOME_DIR}/invalid"),
    ],
)
def it_gets_paths_from_input_when_arg_is_invalid_or_missing(
    mocker: MockerFixture,
    tmp_path: Path,
    path_in: str | None,
) -> None:
    path_in = f"{replace_homedir_with_test_parameter(tmp_path, path_in)}"
    correct_path: str = str(tmp_path.absolute())
    mock_input: Mock = mocker.patch("builtins.input", return_value=correct_path)
    mock_print: Mock = mocker.patch("builtins.print")

    with ScarabTest(argv=["backup", "--source", path_in, "--dest", path_in]) as app:
        app.run()

        mock_input.assert_called_with("Path: ")
        mock_print.assert_called_with(
            {"source": Path(correct_path).absolute(), "dest": Path(correct_path).absolute()}
        )


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
