import os
import pathlib
from importlib import resources
from importlib.abc import Traversable

DATA = resources.files("tests.ytldl2.data")


TEST_CONFIG_DIR: pathlib.Path = pathlib.Path(
    os.path.expanduser(pathlib.Path("~") / ".ytldl2_test_config")
)
TEST_CONFIG_DIR.mkdir(exist_ok=True)

OAUTH_PATH = TEST_CONFIG_DIR / "oauth.json"
