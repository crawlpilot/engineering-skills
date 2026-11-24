"""The HTTP seam the clients call through."""

from typing import Protocol


class Transport(Protocol):
    def get(self, path: str) -> str:
        """Returns the response body. Raises OSError on network failure."""
        ...
