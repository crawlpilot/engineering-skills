"""Exchange-rate client."""

import logging
from decimal import Decimal, InvalidOperation

from rates.errors import ServiceError
from rates.transport import Transport

log = logging.getLogger(__name__)


class RateClient:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def fetch_rate(self, currency: str) -> Decimal:
        """Returns the rate from USD to `currency`, for example Decimal("0.92") for EUR.

        Raises:
            ServiceError: If the rate service can't be reached or returns a malformed rate.
        """
        try:
            body = self._transport.get(f"/rates/{currency}")
        except OSError as exc:
            log.warning("rate lookup failed for %s", currency)
            raise ServiceError(f"could not fetch the {currency} rate") from exc
        try:
            return Decimal(body.strip())
        except InvalidOperation as exc:
            raise ServiceError(f"malformed {currency} rate: {body[:80]!r}") from exc
