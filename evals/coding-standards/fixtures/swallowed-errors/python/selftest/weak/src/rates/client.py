"""Exchange-rate client."""

import logging
from decimal import Decimal

from rates.transport import Transport

log = logging.getLogger(__name__)


class RateClient:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def fetch_rate(self, currency: str) -> Decimal | None:
        """Returns the rate from USD to `currency`, for example Decimal("0.92") for EUR."""
        try:
            body = self._transport.get(f"/rates/{currency}")
            return Decimal(body.strip())
        except Exception:
            log.exception("rate lookup failed")
            return None
