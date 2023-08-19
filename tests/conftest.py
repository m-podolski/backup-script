from pathlib import Path
import pytest
import os


class AppStub:
    def render(self, data: dict[str, str], template: str) -> None:
        pass


@pytest.fixture(scope="function")
def app_fixture() -> AppStub:
    """
    Provides a stub of the cement app-object to set globals.
    """
    return AppStub()


HOME_DIR: str = os.environ["HOME"]


def replace_homedir_with_test_parameter(tmp_path: Path, path_in: str | None) -> str:
    """
    Strips the home-directory (as set in pyproject.toml) and replaces ist with parameters given to the test to enable checking for variable-expansions
    """
    temp_dir: str = f"{tmp_path.parts[3]}/{tmp_path.parts[4]}"
    path: str = f"{path_in}/{temp_dir}"
    return path
