import pytest

slow_test: pytest.MarkDecorator = pytest.mark.skip(reason="slow test")
