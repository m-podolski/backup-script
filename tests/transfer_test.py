from io import TextIOWrapper
from pathlib import Path

import yaml

from app.main import Scarab
from tests.conftest import create_files_and_dirs, make_backup_name


def it_creates_backup_dir(empty_config_fixture: TextIOWrapper, tmp_path: Path) -> None:
    create_files_and_dirs(tmp_path, ["source/", "target/"])
    source: Path = tmp_path / "source"
    target: Path = tmp_path / "target"
    create_files_and_dirs(source, ["dir_1/", "dir_2/", "file.txt"])
    new: Path = target / make_backup_name("source", 2)

    yaml.dump(
        {
            "scarab": {
                "profiles": [
                    {
                        "profile": "test",
                        "source": str(source),
                        "target": str(target),
                        "name": 2,
                    }
                ]
            }
        },
        empty_config_fixture,
    )

    with Scarab(argv=["backup", "profile", "test"]) as app:
        app.run()

        assert new.exists()


def it_updates_backup_dir(empty_config_fixture: TextIOWrapper, tmp_path: Path) -> None:
    create_files_and_dirs(tmp_path, ["source/", "target/"])
    source: Path = tmp_path / "source"
    target: Path = tmp_path / "target"
    create_files_and_dirs(source, ["dir_1/", "dir_2/", "file.txt"])
    create_files_and_dirs(target, [f"{make_backup_name('source', 2)}/", "other/"])
    old: Path = target / make_backup_name("source", 2)
    new: Path = target / make_backup_name("source", 3)

    yaml.dump(
        {
            "scarab": {
                "profiles": [
                    {
                        "profile": "test",
                        "source": str(source),
                        "target": str(target),
                        "name": 3,
                        "ignore_datetime": True,
                    }
                ]
            }
        },
        empty_config_fixture,
    )

    with Scarab(argv=["backup", "profile", "test"]) as app:
        app.run()

        assert not old.exists()
        assert new.exists()
