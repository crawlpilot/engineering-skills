"""An amount of money in a single currency, held to two decimal places."""

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

_CENTS = Decimal("0.01")


@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", self.amount.quantize(_CENTS, rounding=ROUND_HALF_EVEN))

    @classmethod
    def of(cls, amount: str) -> "Money":
        return cls(Decimal(amount))

    def plus(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)
