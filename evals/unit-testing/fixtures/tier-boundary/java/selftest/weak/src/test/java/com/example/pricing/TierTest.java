package com.example.pricing;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

// Deliberately weak suite used only by the fixture self-test: typical values only,
// no boundaries. The grader must score it low.
class TierTest {

  @Test
  void typicalOrderIsStandard() {
    assertThat(Tier.forQuantity(10)).isEqualTo(Tier.STANDARD);
  }

  @Test
  void largeOrderIsBulk() {
    assertThat(Tier.forQuantity(100)).isEqualTo(Tier.BULK);
  }
}
