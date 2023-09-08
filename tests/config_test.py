import filecmp
import os
from pathlib import Path

from app.main import ScarabTest


def it_copies_the_example_config_file_to_user_home() -> None:
    config_file_example: str = f"{os.getcwd()}/assets/example-config.scarab.yml"
    config_file: Path = Path(f"{os.environ['HOME']}/.scarab.yml")

    with ScarabTest(argv=["config", "--create"]) as app:
        app.run()

        assert filecmp.cmp(config_file, config_file_example, shallow=False)

    config_file.unlink()
