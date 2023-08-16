import os
from typing import Optional


def validate_sourcepath(path: str) -> Optional[str]:
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    if os.path.exists(path):
        return path
    else:
        return None
