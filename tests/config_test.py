import filecmp
import os
from io import TextIOWrapper
from pathlib import Path
from unittest.mock import Mock, call

import pytest
import yaml
from pytest_mock import MockerFixture

from app.globals import ScarabError
from app.main import Scarab, ScarabTest
from tests.conftest import create_files_and_dirs, make_backup_name

source_path: Path = Path(__file__).resolve()
config_file_example: str = f"{source_path.parent.parent}/assets/example-config.scarab.yml"


def it_copies_the_example_config_file_to_user_home() -> None:
    config_file: Path = Path(f"{os.environ['HOME']}/.scarab.yml")

    with Scarab(argv=["config", "put"]) as app:
        app.run()

        assert filecmp.cmp(config_file, config_file_example, shallow=False)

    config_file.unlink()


def it_does_not_copy_the_example_file_and_raises_if_a_config_file_is_present(
    config_example_fixture: Path,
) -> None:
    with pytest.raises(
        ScarabError,
        match="A configuration-file is already present at the home-directory",
    ):
        with ScarabTest(argv=["config", "put"]) as app:
            app.run()


def it_overrides_existing_file_with_force_option(
    config_example_fixture: Path,
) -> None:
    config_file: Path = Path(f"{os.environ['HOME']}/.scarab.yml")

    with ScarabTest(argv=["config", "put", "--force"]) as app:
        app.run()

        assert filecmp.cmp(config_file, config_file_example, shallow=False)

    config_file.unlink()


def it_uses_the_config_file_if_an_existing_profile_is_given(
    mocker: MockerFixture,
    empty_config_fixture: TextIOWrapper,
    tmp_path: Path,
) -> None:
    create_files_and_dirs(tmp_path, ["existing_1/", "existing_2/", "file.txt"])
    source_path: Path = Path(f"/home/{os.environ['USER']}")

    yaml.dump(
        {
            "scarab": {
                "profiles": [
                    {
                        "profile": "basic",
                        "mode": "create",
                        "source": str(source_path),
                        "target": str(tmp_path),
                        "name": 5,
                    }
                ]
            }
        },
        empty_config_fixture,
    )

    mock_render: Mock = mocker.patch("app.io.render")

    with Scarab(argv=["backup", "--profile", "basic"]) as app:
        app.run()
        mock_render.assert_has_calls(
            [
                call(
                    "target_contents.jinja2",
                    {
                        "backup_mode": "Create",
                        "source": str(source_path),
                        "target": str(tmp_path),
                        "existing_backup": None,
                        "backup_name": make_backup_name(source_path.name),
                        "target_content": ["existing_1/", "existing_2/", "file.txt"],
                    },
                ),
            ]
        )
