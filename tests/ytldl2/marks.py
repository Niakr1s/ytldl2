import os

import pytest

ALL_TESTS = "ALL" in os.environ

slow_test: pytest.MarkDecorator = pytest.mark.skipif(not ALL_TESTS, reason="slow test")
