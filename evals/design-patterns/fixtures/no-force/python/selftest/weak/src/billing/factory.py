"""Factory and builder for invoices."""

from decimal import Decimal

from billing.invoice import Invoice


class InvoiceFactory:
    @staticmethod
    def create(number: str, customer: str, total: Decimal) -> Invoice:
        return Invoice(number, customer, total)


class InvoiceBuilder:
    def __init__(self) -> None:
        self._number = ""
        self._customer = ""
        self._total = Decimal("0")

    def number(self, value: str) -> "InvoiceBuilder":
        self._number = value
        return self

    def customer(self, value: str) -> "InvoiceBuilder":
        self._customer = value
        return self

    def total(self, value: Decimal) -> "InvoiceBuilder":
        self._total = value
        return self

    def build(self) -> Invoice:
        return InvoiceFactory.create(self._number, self._customer, self._total)
