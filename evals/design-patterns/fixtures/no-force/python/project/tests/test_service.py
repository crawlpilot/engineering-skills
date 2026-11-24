from decimal import Decimal

from billing.invoice import Invoice
from billing.service import create_invoice


def test_numbers_invoices_from_the_sequence():
    assert create_invoice("acme", Decimal("12.50"), 42) == Invoice("INV-00042", "acme", Decimal("12.50"))
