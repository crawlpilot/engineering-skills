# Hidden grading test: the project's own error type is used, as holidays.py does.
import pytest

from rates.client import RateClient
from rates.errors import ServiceError


class Failing:
    def get(self, path: str) -> str:
        raise ConnectionError("connection refused")


def test_uses_the_project_error_type():
    with pytest.raises(ServiceError):
        RateClient(Failing()).fetch_rate("EUR")
