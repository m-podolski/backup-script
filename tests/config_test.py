import datetime
import filecmp
import os
from io import TextIOWrapper
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml
from pytest_mock import MockerFixture

from app.globals import ScarabArgumentError, ScarabError, ScarabOptionError
from app.main import Scarab, ScarabTest
from tests.conftest import create_files_and_dirs, make_backup_name_format

source_path: Path = Path(__file__).resolve()
config_file_example: str = f"{source_path.parent.parent}/assets/example-config.scarab.yml"


def it_copies_the_example_config_file_to_user_home() -> None:
    config_file: Path = Path(f"{os.environ['HOME']}/.scarab.yml")

    with ScarabTest(argv=["config", "put"]) as app:
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


def it_raises_if_config_is_missing_required_args(
    empty_config_fixture: TextIOWrapper,
) -> None:
    yaml.dump(
        {
            "scarab": {
                "profiles": [
                    {
                        "profile": "basic",
                        "source": "~",
                        "name": 5,
                    }
                ]
            }
        },
        empty_config_fixture,
    )

    with pytest.raises(
        ScarabOptionError,
        match=f": Your config-file is missing a required option: 'target'",
    ):
        with Scarab(argv=["backup", "profile", "basic"]) as app:
            app.run()


def it_raises_argument_error_if_given_an_invalid_path(
    empty_config_fixture: TextIOWrapper,
    tmp_path: Path,
) -> None:
    yaml.dump(
        {
            "scarab": {
                "profiles": [
                    {
                        "profile": "basic",
                        "source": str(tmp_path / "invalid"),
                        "target": str(tmp_path),
                        "name": 5,
                    }
                ]
            }
        },
        empty_config_fixture,
    )
    with pytest.raises(
        ScarabArgumentError,
        match=": A location has an invalid path",
    ):
        with Scarab(argv=["backup", "profile", "basic"]) as app:
            app.run()


def it_uses_the_config_file_if_an_existing_profile_is_given(
    mocker: MockerFixture,
    empty_config_fixture: TextIOWrapper,
    tmp_path: Path,
) -> None:
    create_files_and_dirs(tmp_path, ["source/", "target/"])
    create_files_and_dirs(tmp_path / "target", ["other/"])

    yaml.dump(
        {
            "scarab": {
                "profiles": [
                    {
                        "profile": "basic",
                        "source": str(tmp_path / "source"),
                        "target": str(tmp_path / "target"),
                        "name": 5,
                    }
                ]
            }
        },
        empty_config_fixture,
    )

    mock_render: Mock = mocker.patch("app.io.render")

    with Scarab(argv=["backup", "profile", "basic"]) as app:
        app.run()

        assert mock_render.mock_calls[0].args[1]["target"] == str(tmp_path / "target")
        assert mock_render.mock_calls[0].args[1]["existing_backup"] == None
        assert mock_render.mock_calls[0].args[1]["backup_name"] == make_backup_name_format(
            "source", 5
        )


def it_selects_an_existing_backup_by_name_format(
    mocker: MockerFixture,
    empty_config_fixture: TextIOWrapper,
    tmp_path: Path,
) -> None:
    create_files_and_dirs(tmp_path, ["source/", "target/"])
    existing_backup: str = make_backup_name_format("source", 5)
    create_files_and_dirs(
        tmp_path / "target",
        [
            f"{existing_backup}/",
            f"{make_backup_name_format('other', 5)}/",
        ],
    )

    yaml.dump(
        {
            "scarab": {
                "profiles": [
                    {
                        "profile": "basic",
                        "source": str(tmp_path / "source"),
                        "target": str(tmp_path / "target"),
                        "name": 5,
                    }
                ]
            }
        },
        empty_config_fixture,
    )

    mock_render: Mock = mocker.patch("app.io.render")

    with Scarab(argv=["backup", "profile", "basic"]) as app:
        app.run()

        assert mock_render.mock_calls[0].args[1]["target"] == str(tmp_path / "target")
        assert mock_render.mock_calls[0].args[1]["existing_backup"] == existing_backup
        assert mock_render.mock_calls[0].args[1]["backup_name"] == make_backup_name_format(
            "source", 5
        )


def it_selects_an_existing_backup_ignoring_the_date_if_configured(
    mocker: MockerFixture,
    empty_config_fixture: TextIOWrapper,
    tmp_path: Path,
) -> None:
    create_files_and_dirs(tmp_path, ["source/", "target/"])
    existing_backup_older: str = make_backup_name_format("source", 5, datetime.datetime(2023, 9, 1))
    existing_backup_newer: str = make_backup_name_format("source", 5, datetime.datetime(2023, 9, 2))
    other_backup_newer: str = make_backup_name_format("other", 5)
    other_backup_older: str = make_backup_name_format("other", 5, datetime.datetime(2023, 9, 2))
    create_files_and_dirs(
        tmp_path / "target",
        [
            f"{existing_backup_older}/",
            f"{existing_backup_newer}/",
            f"{other_backup_older}/",
            f"{other_backup_newer}/",
        ],
    )

    yaml.dump(
        {
            "scarab": {
                "profiles": [
                    {
                        "profile": "basic",
                        "source": str(tmp_path / "source"),
                        "target": str(tmp_path / "target"),
                        "name": 5,
                        "ignore_datetime": True,
                    }
                ]
            }
        },
        empty_config_fixture,
    )

    mock_render: Mock = mocker.patch("app.io.render")

    with Scarab(argv=["backup", "profile", "basic"]) as app:
        app.run()

        assert mock_render.mock_calls[0].args[1]["target"] == str(tmp_path / "target")
        assert mock_render.mock_calls[0].args[1]["existing_backup"] == existing_backup_newer
        assert mock_render.mock_calls[0].args[1]["backup_name"] == make_backup_name_format(
            "source", 5
        )
