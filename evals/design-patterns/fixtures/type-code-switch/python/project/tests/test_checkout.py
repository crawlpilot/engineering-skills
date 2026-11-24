from decimal import Decimal

import pytest

from payments.checkout import quote
from payments.methods import PaymentMethod


@pytest.mark.parametrize(
    ("method", "fee", "days", "refundable"),
    [
        (PaymentMethod.CARD, "2.90", 2, True),
        (PaymentMethod.BANK_TRANSFER, "0.80", 3, True),
        (PaymentMethod.WALLET, "1.50", 1, False),
        (PaymentMethod.VOUCHER, "0.00", 0, False),
    ],
)
def test_quotes_each_method(method, fee, days, refundable):
    q = quote(method, Decimal("100"))
    assert (q.fee, q.settlement_days, q.refundable) == (Decimal(fee), days, refundable)
