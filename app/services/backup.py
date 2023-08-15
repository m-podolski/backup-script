import os


def validate_sourcepath(path: str) -> bool:
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)

    return os.path.exists(path)
