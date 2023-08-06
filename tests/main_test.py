from cement import TestApp
from app import Scarab


class ScarabTest(TestApp, Scarab):
    class Meta:
        label = "scarabTest"


def test_debug_flag():
    with ScarabTest() as app:
        assert app.debug is False

    with ScarabTest(argv=["--debug"]) as app:
        assert app.debug is True
