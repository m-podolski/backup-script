from typing import Optional

BackupMode = Optional[str]


def validate_sourcepath(path: str) -> bool:
    print("validate_sourcepath")
    return True


def read_sourcepath() -> None:
    print("Enter your source directory (absolute path): ")
