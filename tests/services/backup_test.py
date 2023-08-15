from app.services.backup import validate_sourcepath


def test_validate_sourcepath() -> None:
    valid: bool = validate_sourcepath("/path")
    assert valid is True
