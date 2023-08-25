import os
from pathlib import Path

HOME: str = os.environ["HOME"]
USER: str = os.environ["USER"]


def replace_homedir_with_test_parameter(tmp_path: Path, path_in: str | None) -> str:
    """
    Strips the home-directory (as set in pyproject.toml) and replaces ist with parameters given to the test to enable checking for variable-expansions
    """
    temp_dir: str = f"{tmp_path.parts[3]}/{tmp_path.parts[4]}"
    path: str = f"{path_in}/{temp_dir}"
    return path
