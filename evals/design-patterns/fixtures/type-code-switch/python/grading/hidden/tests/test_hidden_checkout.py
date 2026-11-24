# Hidden grading test: behaviour of every method is unchanged.
from decimal import Decimal

import pytest

from payments.checkout import quote
from payments.methods import PaymentMethod


@pytest.mark.parametrize(
    ("method", "fee", "days", "refundable"),
    [
        (PaymentMethod.CARD, "7.25", 2, True),
        (PaymentMethod.BANK_TRANSFER, "2.00", 3, True),
        (PaymentMethod.WALLET, "3.75", 1, False),
        (PaymentMethod.VOUCHER, "0.00", 0, False),
    ],
)
def test_hidden_quotes_each_method(method, fee, days, refundable):
    q = quote(method, Decimal("250"))
    assert (q.fee, q.settlement_days, q.refundable) == (Decimal(fee), days, refundable)
