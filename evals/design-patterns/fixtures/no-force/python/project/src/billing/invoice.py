"""Invoices."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Invoice:
    number: str
    customer: str
    total: Decimal
