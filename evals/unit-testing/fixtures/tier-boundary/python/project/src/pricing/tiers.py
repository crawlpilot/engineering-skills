"""Price tiers for orders, chosen by the number of items in them."""

from enum import Enum

# Orders of this many items or more are priced as bulk.
BULK_THRESHOLD = 50


class Tier(Enum):
    FREE = "free"
    STANDARD = "standard"
    BULK = "bulk"


def tier_for_quantity(quantity: int) -> Tier:
    """Returns the tier for an order quantity.

    - 0 items: FREE
    - 1 to 49 items: STANDARD
    - 50 items or more: BULK

    Raises:
        ValueError: If quantity is negative.
    """
    if quantity < 0:
        raise ValueError(f"quantity must not be negative: {quantity}")
    if quantity == 0:
        return Tier.FREE
    if quantity > BULK_THRESHOLD:
        return Tier.BULK
    return Tier.STANDARD
