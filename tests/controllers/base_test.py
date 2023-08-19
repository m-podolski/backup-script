from pathlib import Path
from unittest.mock import Mock
import pytest
from pytest_mock import MockerFixture
from app.exceptions import ScarabArgumentError

from app.main import ScarabTest
from app.controllers.base import Base
from tests.conftest import AppStub, HOME_DIR, replace_homedir_with_test_parameter


@pytest.fixture()
def controller_fixture(app_fixture: AppStub) -> Base:
    """
    Provides the controller instance and sets .app
    """
    controller = Base()
    setattr(controller, "app", app_fixture)
    return controller


def test_backup(mocker: MockerFixture) -> None:
    mock_check_sourcepath: Mock = mocker.patch("app.controllers.base.Base._check_sourcepath")

    with ScarabTest(argv=["backup"]) as app:  # pyright: ignore
        app.run()
        mock_check_sourcepath.assert_called_with(None)

    with ScarabTest(argv=["backup", "--source", "/path"]) as app:
        app.run()
        mock_check_sourcepath.assert_called_with("/path")


@pytest.mark.parametrize(
    "path_in",
    [
        (None),
        (f"{HOME_DIR}"),
        (f"{HOME_DIR}/invalid_48zfhbn0934jf"),
        ("~"),
        ("$HOME"),
    ],
)
def test_check_sourcepath(
    mocker: MockerFixture,
    controller_fixture: Base,
    tmp_path: Path,
    path_in: str | None,
) -> None:
    correct_path: str = str(tmp_path.absolute())
    mocker.patch.object(controller_fixture, attribute="_read_sourcepath", return_value=correct_path)

    if path_in is None:
        path_checked: Path = controller_fixture._check_sourcepath(path_in)  # pyright: ignore
    else:
        path: str = replace_homedir_with_test_parameter(tmp_path, path_in)
        path_checked: Path = controller_fixture._check_sourcepath(path)  # pyright: ignore

    assert path_checked == Path(correct_path)


def test_read_sourcepath(mocker: MockerFixture, controller_fixture: Base) -> None:
    user_input: str = "/path"
    mocker.patch("builtins.input", return_value=user_input)

    path_read: str = controller_fixture._read_sourcepath("Some Message")  # pyright: ignore

    assert path_read == user_input


def test_read_sourcepath_raises_in_quiet_mode(
    mocker: MockerFixture, controller_fixture: Base
) -> None:
    mocker.patch("builtins.input")
    controller_fixture.app.quiet = False  # pyright: ignore

    controller_fixture._read_sourcepath("msg")  # pyright: ignore

    with pytest.raises(
        ScarabArgumentError,
        match=r"^Scarab got wrong or conflicting arguments: Cannot receive input in quiet mode",
    ):
        controller_fixture.app.quiet = True  # pyright: ignore
        controller_fixture._read_sourcepath("msg")  # pyright: ignore
