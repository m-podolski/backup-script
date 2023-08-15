from unittest.mock import Mock
import pytest
from pytest_mock import MockerFixture

from app.main import ScarabTest
from app.controllers.base import Base
from tests.conftest import AppStub


@pytest.fixture()
def controller_fixture(app_fixture: AppStub) -> Base:
    controller = Base()
    setattr(controller, "app", app_fixture)
    return controller


def test_backup(mocker: MockerFixture) -> None:
    spy_check_sourcepath: Mock = mocker.patch("app.controllers.base.Base._check_sourcepath")

    with ScarabTest(argv=["backup"]) as app:  # pyright: ignore
        app.run()
        spy_check_sourcepath.assert_called_with(None)

    with ScarabTest(argv=["backup", "--source", "/path"]) as app:
        app.run()
        spy_check_sourcepath.assert_called_with("/path")


valid_sourcepath = "~/dev"


@pytest.mark.parametrize(
    "path_in, path_out, read_sourcepath_call_count",
    [
        (None, valid_sourcepath, 1),
        ("/invalid", valid_sourcepath, 1),
        (valid_sourcepath, valid_sourcepath, 0),
    ],
)
def test_check_sourcepath(
    mocker: MockerFixture,
    controller_fixture: Base,
    path_in: str | None,
    path_out: str,
    read_sourcepath_call_count: int,
) -> None:
    mock_read_sourcepath: Mock = mocker.patch.object(
        controller_fixture, attribute="_read_sourcepath", return_value=valid_sourcepath
    )

    path_checked: str = (
        controller_fixture._check_sourcepath(  # pyright: ignore [reportPrivateUsage]
            path_in  # pyright: ignore
        )
    )
    assert path_checked == path_out
    assert mock_read_sourcepath.call_count == read_sourcepath_call_count
    mock_read_sourcepath.reset_mock()
