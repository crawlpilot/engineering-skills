"""In-memory order store."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    id: int
    customer: str
    status: str  # "open", "shipped" or "cancelled"


class OrderStore:
    def __init__(self) -> None:
        self._orders: list[Order] = []

    def add(self, order: Order) -> None:
        self._orders.append(order)

    def get(self, order_id: int) -> Order | None:
        return next((o for o in self._orders if o.id == order_id), None)

    def all(self) -> list[Order]:
        """Returns every order, oldest first."""
        return list(self._orders)
