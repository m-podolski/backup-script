from app.main import ScarabTest


def test_debug_flag():
    with ScarabTest() as app:
        assert app.debug is False

    with ScarabTest(argv=["--debug"]) as app:
        assert app.debug is True
