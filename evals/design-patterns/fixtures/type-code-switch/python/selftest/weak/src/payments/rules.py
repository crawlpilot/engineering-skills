"""Per-method business rules."""

from decimal import Decimal

from payments.methods import PaymentMethod

_FEES = {PaymentMethod.CARD: Decimal("2.9"), PaymentMethod.BANK_TRANSFER: Decimal("0.8"),
         PaymentMethod.WALLET: Decimal("1.5")}
_DAYS = {PaymentMethod.CARD: 2, PaymentMethod.BANK_TRANSFER: 3, PaymentMethod.WALLET: 1}
_REFUNDABLE = {PaymentMethod.CARD, PaymentMethod.BANK_TRANSFER}


def fee_percent(method: PaymentMethod) -> Decimal:
    """Processing fee, as a percentage of the amount."""
    return _FEES.get(method, Decimal("0"))


def settlement_days(method: PaymentMethod) -> int:
    """Working days until the money reaches the merchant."""
    return _DAYS.get(method, 0)


def refundable(method: PaymentMethod) -> bool:
    """Whether a payment by this method can be refunded to the same method."""
    return method in _REFUNDABLE
