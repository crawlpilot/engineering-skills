"""Errors raised by the service clients in this package."""


class ServiceError(Exception):
    """A call to an upstream service failed. The message names what was being fetched."""
