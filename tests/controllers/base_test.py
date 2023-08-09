from app.main import Scarab, ScarabTest
from app.controllers import base


def test_backup(mocker):
    spy = mocker.spy(base, "run_backup")

    with ScarabTest(argv=["backup"]) as app:
        app.run()
        spy.assert_called_with(None, None)

    with ScarabTest(argv=["backup", "--source", "/path"]) as app:
        app.run()
        spy.assert_called_with("/path", None)

    with ScarabTest(argv=["backup", "--source", "/path", "--create"]) as app:
        app.run()
        spy.assert_called_with("/path", "CREATE")
