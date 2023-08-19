import pytest
from app.services.backup import validate_sourcepath
from tests.conftest import Temp, HOME_DIR


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
    temp_dir_fixture: Temp,
    path_in: str,
    valid: bool,
) -> None:
    path: str = f"{path_in}/{temp_dir_fixture.dirname}"
    if valid:
        assert isinstance(validate_sourcepath(path), str)
    else:
        assert validate_sourcepath(path) == None
