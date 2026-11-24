"""Creates invoices. This is the only place an Invoice is constructed."""

from decimal import Decimal

from billing.invoice import Invoice


def create_invoice(customer: str, total: Decimal, sequence: int) -> Invoice:
    return Invoice(number=f"INV-{sequence:05d}", customer=customer, total=total)
