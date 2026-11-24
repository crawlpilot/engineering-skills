# Hidden grading tests: copied in by the grader, never shown to the agent.
from decimal import Decimal

import pytest

from rates.client import RateClient
from rates.errors import ServiceError


class Failing:
    def __init__(self, exc: BaseException) -> None:
        self.exc = exc

    def get(self, path: str) -> str:
        raise self.exc


class Body:
    def __init__(self, body: str) -> None:
        self.body = body

    def get(self, path: str) -> str:
        return self.body


def chain(exc: BaseException) -> list[BaseException]:
    seen = []
    while exc is not None and exc not in seen:
        seen.append(exc)
        exc = exc.__cause__ or exc.__context__
    return seen


def test_success_still_returns_the_rate():
    assert RateClient(Body("0.92\n")).fetch_rate("EUR") == Decimal("0.92")


def test_network_failure_raises_with_context_and_cause():
    original = ConnectionError("connection refused")
    with pytest.raises(Exception) as info:
        RateClient(Failing(original)).fetch_rate("EUR")
    assert "EUR" in " ".join(str(e) for e in chain(info.value))
    assert original in chain(info.value)


def test_malformed_body_raises_with_context():
    with pytest.raises(Exception) as info:
        RateClient(Body("n/a")).fetch_rate("EUR")
    assert "EUR" in " ".join(str(e) for e in chain(info.value))


def test_programming_errors_are_not_swallowed():
    with pytest.raises(TypeError):
        RateClient(Failing(TypeError("bug"))).fetch_rate("EUR")
