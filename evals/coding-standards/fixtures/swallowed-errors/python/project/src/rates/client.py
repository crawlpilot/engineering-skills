"""Exchange-rate client."""

from decimal import Decimal

from rates.transport import Transport


class RateClient:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def fetch_rate(self, currency: str) -> Decimal | None:
        """Returns the rate from USD to `currency`, for example Decimal("0.92") for EUR."""
        try:
            body = self._transport.get(f"/rates/{currency}")
            return Decimal(body.strip())
        except Exception:
            return None
