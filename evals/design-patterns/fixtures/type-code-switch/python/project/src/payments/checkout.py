"""Prices a payment for the checkout page."""

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

from payments import rules
from payments.methods import PaymentMethod


@dataclass(frozen=True)
class Quote:
    fee: Decimal
    settlement_days: int
    refundable: bool


def quote(method: PaymentMethod, amount: Decimal) -> Quote:
    fee = (amount * rules.fee_percent(method) / 100).quantize(Decimal("0.01"), ROUND_HALF_EVEN)
    return Quote(fee, rules.settlement_days(method), rules.refundable(method))
