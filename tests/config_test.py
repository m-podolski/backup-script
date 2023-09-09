import filecmp
import os
from pathlib import Path

import pytest

from app.globals import ScarabError
from app.main import ScarabTest

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
