import datetime
import os
import shutil
import socket
from io import TextIOWrapper
from pathlib import Path
from typing import Generator, Optional

import pytest


@pytest.fixture
def media_dir_fixture(
    tmp_path: Path,
) -> Generator[Path, None, None]:
    """
    Provides a location to test media-flag-functionality against. To use it pass it in as argument to --target. The app will detect the test by matching against "^/tmp/pytest.+media$".
    """
    media_dir: Path = tmp_path / "media"
    media_dir.mkdir()

    yield media_dir


@pytest.fixture
def config_example_fixture() -> Generator[Path, None, None]:
    """
    Sets up and tears down a config-file based on the example-file provided to users.
    """
    source_path: Path = Path(__file__).resolve()
    config_file_example: str = f"{source_path.parent.parent}/assets/example-config.scarab.yml"
    config_file: Path = Path(f"{os.environ['HOME']}/.scarab.yml")
    shutil.copyfile(config_file_example, config_file)

    yield config_file

    config_file.unlink()


@pytest.fixture
def empty_config_fixture() -> Generator[TextIOWrapper, None, None]:
    """
    Sets up and tears down an empty config-file.
    """
    config_file: Path = Path(f"{os.environ['HOME']}/.scarab.yml")
    config_file.touch()

    with open(config_file, "w") as file:
        yield file

    config_file.unlink()


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


def make_backup_name(
    source_dir: str, name_arg: int, set_date: Optional[datetime.datetime] = None
) -> str:
    user: str = os.environ["USER"]
    host: str = socket.gethostname()
    date: str = (
        set_date.strftime("%Y-%m-%d")
        if set_date
        else datetime.datetime.today().strftime("%Y-%m-%d")
    )
    time: str = (
        set_date.strftime("%H-%M-%S")
        if set_date
        else datetime.datetime.today().strftime("%H-%M-%S")
    )

    name_formats: list[str] = [
        source_dir,
        f"{source_dir}_{date}",
        f"{source_dir}_{date}-{time}",
        f"{user}@{host}_{source_dir}",
        f"{user}@{host}_{source_dir}_{date}",
        f"{user}@{host}_{source_dir}_{date}-{time}",
    ]

    return name_formats[name_arg - 1]
