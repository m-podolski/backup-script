class ScarabException(Exception):
    pass


class ScarabArgumentError(ScarabException):
    def __init__(self, message: str) -> None:
        super().__init__(f"Scarab got wrong or conflicting arguments: {message}")
