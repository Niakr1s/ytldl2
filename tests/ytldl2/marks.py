import pytest

SKIP_SLOW_TESTS = True

slow_test: pytest.MarkDecorator = pytest.mark.skipif(
    SKIP_SLOW_TESTS, reason="slow test"
)
