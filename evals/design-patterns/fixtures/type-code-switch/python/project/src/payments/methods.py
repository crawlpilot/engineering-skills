"""How a customer pays."""

from enum import Enum


class PaymentMethod(Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    VOUCHER = "voucher"
