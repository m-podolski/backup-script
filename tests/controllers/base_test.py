from pytest_mock import MockerFixture

from app.main import ScarabTest
from app.controllers import base


class Bla:
    @staticmethod
    def blub() -> None:
        pass


def test_backup(mocker: MockerFixture) -> None:
    spy_validate_sourcepath = mocker.spy(base, "validate_sourcepath")
    spy_read_sourcepath = mocker.spy(base, "read_sourcepath")

    with ScarabTest(argv=["backup"]) as app:  # pyright: ignore
        app.run()
        spy_read_sourcepath.assert_called_with()

    with ScarabTest(argv=["backup", "--source", "/path"]) as app:
        app.run()
        spy_validate_sourcepath.assert_called_with("/path")
