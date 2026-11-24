"""Bank holiday client."""

import json
import logging

from rates.errors import ServiceError
from rates.transport import Transport

log = logging.getLogger(__name__)


class HolidayClient:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def holidays(self, country: str) -> list[str]:
        """Returns the ISO dates of bank holidays this year in `country`."""
        try:
            body = self._transport.get(f"/holidays/{country}")
        except OSError as exc:
            log.warning("holiday lookup failed for %s", country)
            raise ServiceError(f"could not fetch holidays for {country}") from exc
        try:
            return [str(d) for d in json.loads(body)]
        except (ValueError, TypeError) as exc:
            raise ServiceError(f"malformed holiday list for {country}: {body[:80]!r}") from exc
