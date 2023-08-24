from app.main import ScarabTest


def test_debug_flag() -> None:
    with ScarabTest() as app:
        assert app.debug is False  # pyright: ignore

    with ScarabTest(argv=["--debug"]) as app:
        assert app.debug is True  # pyright: ignore
