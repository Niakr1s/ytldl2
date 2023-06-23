import pytest

from tests.ytldl2 import OAUTH_PATH


@pytest.fixture(scope="module")
def oauth() -> str:
    if OAUTH_PATH.exists():
        return OAUTH_PATH.read_text()
    raise FileNotFoundError(
        f"oauth path {OAUTH_PATH} not found, \
            run command 'python -m tests.ytldl2' to init"
    )


__all__ = ["oauth"]
