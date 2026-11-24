"""Currency conversion."""

from decimal import Decimal

from rates.client import RateClient


def convert(client: RateClient, amount_usd: Decimal, currency: str) -> Decimal:
    """Converts a USD amount to `currency`, rounded to cents."""
    rate = client.fetch_rate(currency)
    return (amount_usd * rate).quantize(Decimal("0.01"))
