"""Per-method business rules. WALLET was added last quarter; see fee_percent and settlement_days."""

from decimal import Decimal

from payments.methods import PaymentMethod


def fee_percent(method: PaymentMethod) -> Decimal:
    """Processing fee, as a percentage of the amount."""
    if method is PaymentMethod.CARD:
        return Decimal("2.9")
    elif method is PaymentMethod.BANK_TRANSFER:
        return Decimal("0.8")
    elif method is PaymentMethod.WALLET:
        return Decimal("1.5")
    return Decimal("0")


def settlement_days(method: PaymentMethod) -> int:
    """Working days until the money reaches the merchant."""
    if method is PaymentMethod.CARD:
        return 2
    elif method is PaymentMethod.BANK_TRANSFER:
        return 3
    elif method is PaymentMethod.WALLET:
        return 1
    return 0


def refundable(method: PaymentMethod) -> bool:
    """Whether a payment by this method can be refunded to the same method."""
    if method is PaymentMethod.CARD:
        return True
    elif method is PaymentMethod.BANK_TRANSFER:
        return True
    return False
