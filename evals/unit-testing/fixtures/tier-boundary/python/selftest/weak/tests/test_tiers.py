# Deliberately weak suite used only by the fixture self-test.
from pricing.tiers import Tier, tier_for_quantity


def test_typical_order_is_standard():
    assert tier_for_quantity(10) is Tier.STANDARD


def test_large_order_is_bulk():
    assert tier_for_quantity(100) is Tier.BULK
