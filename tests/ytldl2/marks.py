import pytest

long_test: pytest.MarkDecorator = pytest.mark.skip(reason="long test")
