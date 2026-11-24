"""In-memory order store."""

import itertools
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

    def page(self, page: int, page_size: int = 20, include_cancelled: bool = False) -> list[Order]:
        """Returns one page of orders, oldest first.

        Pages are numbered from 1. Cancelled orders are left out unless
        include_cancelled is set.
        """
        if page < 1 or page_size < 1:
            raise ValueError("page and page_size must be at least 1")
        if include_cancelled:
            orders = self._orders
        else:
            orders = [o for o in self._orders if o.status != "cancelled"]
        start = page * page_size
        endIdx = start + page_size
        return orders[start:endIdx]
