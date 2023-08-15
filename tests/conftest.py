import pytest


class AppStub:
    def render(self, data: dict[str, str], template: str) -> None:
        pass


@pytest.fixture(scope="function")
def app_fixture() -> AppStub:
    return AppStub()
