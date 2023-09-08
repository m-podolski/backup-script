from pathlib import Path
from typing import Any, Generator

import pytest


@pytest.fixture
def media_dir_fixture(
    tmp_path: Path,
) -> Generator[Any, Any, None]:
    """
    Provides a location to test media-flag-functionality against. To use it pass it in as argument to --target. The app will detect the test by matching against "^/tmp/pytest.+media$".
    """
    media_dir: Path = tmp_path / "media"
    media_dir.mkdir()

    yield media_dir


@pytest.fixture
def config_example_fixture() -> Generator[Any, Any, None]:
    """
    Sets up and tears down a config-file based on the example-file provided to users.
    """
    media_dir: Path = tmp_path / "media"
    media_dir.mkdir()

    yield media_dir


def create_files_and_dirs(path: Path, items: list[str]) -> None:
    """
    Populates a given path. To distinguish between files and directories within the items, append a slash to directories (i.e. ["dir/", "file"])
    """
    for item in items:
        path_to_create: Path = path / item
        if item[len(item) - 1] == "/":
            path_to_create.mkdir()
        else:
            path_to_create.touch()


def get_content_with_slashed_dirs(dir: Path) -> list[str]:
    def slash(path: Path) -> str:
        if path.is_dir():
            return f"{path.name}/"
        else:
            return path.name

    return [slash(path) for path in dir.iterdir()]
