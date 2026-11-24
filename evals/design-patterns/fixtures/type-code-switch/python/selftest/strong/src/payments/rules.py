"""Per-method business rules. Kept for existing callers; the table lives in methods.py."""

from decimal import Decimal

from payments.methods import RULES, PaymentMethod


def fee_percent(method: PaymentMethod) -> Decimal:
    """Processing fee, as a percentage of the amount."""
    return RULES[method].fee_percent


def settlement_days(method: PaymentMethod) -> int:
    """Working days until the money reaches the merchant."""
    return RULES[method].settlement_days


def refundable(method: PaymentMethod) -> bool:
    """Whether a payment by this method can be refunded to the same method."""
    return RULES[method].refundable
