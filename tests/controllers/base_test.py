from unittest.mock import Mock
import pytest
from pytest_mock import MockerFixture

from app.main import ScarabTest
from app.controllers.base import Base
from tests.conftest import AppStub, Temp, home_dir


@pytest.fixture()
def controller_fixture(app_fixture: AppStub) -> Base:
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
        (f"{home_dir}"),
        (f"{home_dir}/invalid_48zfhbn0934jf"),
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

    path_checked: str | bool = (
        controller_fixture._check_sourcepath(  # pyright: ignore [reportPrivateUsage]
            f"{path_in}/{temp_dir_fixture.dirname}"  # pyright: ignore
        )
    )
    assert path_checked == temp_dir_fixture.path
