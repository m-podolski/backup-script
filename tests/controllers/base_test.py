from unittest.mock import Mock
import pytest
from pytest_mock import MockerFixture

from app.main import ScarabTest
from app.controllers.base import Base
from tests.conftest import AppStub, Temp, HOME_DIR


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
    ],
)
def test_check_sourcepath(
    mocker: MockerFixture,
    controller_fixture: Base,
    temp_dir_fixture: Temp,
    path_in: str | None,
) -> None:
    mocker.patch.object(
        controller_fixture, attribute="_read_sourcepath", return_value=temp_dir_fixture.path
    )

    path_checked: str | bool = controller_fixture._check_sourcepath(  # pyright: ignore
        f"{path_in}/{temp_dir_fixture.dirname}"  # pyright: ignore
    )
    assert path_checked == temp_dir_fixture.path


def test_read_sourcepath(mocker: MockerFixture, controller_fixture: Base) -> None:
    user_input: str = "/path"
    mocker.patch("builtins.input", return_value=user_input)

    path_read: str = controller_fixture._read_sourcepath("Some Message")  # pyright: ignore

    assert path_read == user_input
