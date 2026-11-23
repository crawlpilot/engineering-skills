# Known-good suite used only by the fixture self-test.
import sys

import pytest

from pricing.tiers import Tier, tier_for_quantity


@pytest.mark.parametrize(
    ("quantity", "expected"),
    [
        (0, Tier.FREE),
        (1, Tier.STANDARD),
        (49, Tier.STANDARD),
        (50, Tier.BULK),
        (sys.maxsize, Tier.BULK),
    ],
)
def test_picks_tier_by_quantity(quantity, expected):
    assert tier_for_quantity(quantity) is expected


def test_rejects_minus_one():
    with pytest.raises(ValueError, match="negative"):
        tier_for_quantity(-1)
