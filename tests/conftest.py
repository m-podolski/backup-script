from pathlib import Path
from typing import Any, Generator

import pytest


@pytest.fixture
def media_dir_fixture(
    tmp_path: Path,
) -> Generator[Any, Any, None]:
    """
    Provides a location to test media-flag-functionality against. To use it pass it in as argument to --dest. The app will detect the test by matching against "^/tmp/pytest.+media$".
    """
    media_dir: Path = tmp_path / "media"
    media_dir.mkdir()
    dir1: Path = media_dir / "directory_1"
    dir2: Path = media_dir / "directory_2"
    dir2.mkdir()
    dir1.mkdir()

    yield media_dir


def get_content_with_slashed_dirs(dir: Path) -> list[str]:
    def slash(path: Path) -> str:
        if path.is_dir():
            return f"{path.name}/"
        else:
            return path.name

    return [slash(path) for path in dir.iterdir()]
