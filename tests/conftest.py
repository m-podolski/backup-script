from typing import Any, Generator
import pytest
import os
import shutil
from tempfile import mkdtemp


class AppStub:
    def render(self, data: dict[str, str], template: str) -> None:
        pass


@pytest.fixture(scope="function")
def app_fixture() -> AppStub:
    return AppStub()


home_dir: str = os.environ["HOME"]


class Temp:
    """
    Creates temporary directories. It uses the home-dir as root to enable testing for tilde- and var-expansions.
    """

    def __init__(self) -> None:
        self.path: str = mkdtemp(dir=f"{home_dir}")
        self.dirname: str = self.path[-len(home_dir) : :]


@pytest.fixture(scope="function")
def temp_dir_fixture() -> Generator[Temp, Any, None]:
    temp = Temp()
    yield temp

    if os.path.exists(temp.path):
        shutil.rmtree(temp.path)
