"""How a customer pays, with the rules for each method."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


@dataclass(frozen=True)
class Rules:
    fee_percent: Decimal
    settlement_days: int
    refundable: bool


class PaymentMethod(Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    VOUCHER = "voucher"


# Every method must appear here. The check below fails at import time if one is
# missing, so a new method can't ship with default rules.
RULES: dict[PaymentMethod, Rules] = {
    PaymentMethod.CARD: Rules(Decimal("2.9"), 2, True),
    PaymentMethod.BANK_TRANSFER: Rules(Decimal("0.8"), 3, True),
    PaymentMethod.WALLET: Rules(Decimal("1.5"), 1, False),
    PaymentMethod.VOUCHER: Rules(Decimal("0"), 0, False),
}
_missing = set(PaymentMethod) - set(RULES)
if _missing:
    raise RuntimeError(f"no rules for payment methods: {sorted(m.name for m in _missing)}")
