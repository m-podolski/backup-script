import os
import shutil
from pathlib import Path

from app.globals import ScarabError


def put_example() -> None:
    source_path: Path = Path(__file__).resolve()
    config_file_example: str = f"{source_path.parent.parent}/assets/example-config.scarab.yml"
    config_file: Path = Path(f"{os.environ['HOME']}/.scarab.yml")

    if config_file.exists():
        raise ScarabError("A configuration-file is already present at the home-directory")

    shutil.copyfile(config_file_example, config_file)
