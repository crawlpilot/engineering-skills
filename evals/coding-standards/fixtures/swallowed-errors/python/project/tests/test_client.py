from decimal import Decimal

from rates.client import RateClient
from rates.convert import convert


class FakeTransport:
    def __init__(self, body: str) -> None:
        self.body = body

    def get(self, path: str) -> str:
        return self.body


def test_parses_rate():
    assert RateClient(FakeTransport("0.92\n")).fetch_rate("EUR") == Decimal("0.92")


def test_converts_amount():
    assert convert(RateClient(FakeTransport("0.92")), Decimal("10"), "EUR") == Decimal("9.20")
