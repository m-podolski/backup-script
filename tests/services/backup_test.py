from pathlib import Path
import pytest
from app.services.backup import validate_sourcepath
from tests.conftest import HOME_DIR, replace_homedir_with_test_parameter


@pytest.mark.parametrize(
    "path_in, valid",
    [
        (f"{HOME_DIR}", True),
        (f"{HOME_DIR}/invalid_48zfhbn0934jf", False),
        ("~", True),
        ("$HOME", True),
    ],
)
def test_validate_sourcepath(
    tmp_path: Path,
    path_in: str,
    valid: bool,
) -> None:
    path: str = replace_homedir_with_test_parameter(tmp_path, path_in)
    if valid:
        assert isinstance(validate_sourcepath(path), str)
    else:
        assert validate_sourcepath(path) == None
