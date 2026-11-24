from decimal import Decimal

from pricing.money import Money


def test_rounds_to_two_decimal_places():
    assert Money.of("10.005").amount == Decimal("10.00")


def test_adds_amounts():
    assert Money.of("1.10").plus(Money.of("2.25")) == Money.of("3.35")
