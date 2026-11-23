package com.example.pricing;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

// Known-good suite used only by the fixture self-test. It must pass on the
// reference, fail on the planted bug and kill every mutant.
class TierTest {

  @ParameterizedTest
  @CsvSource({
    "0,          FREE",
    "1,          STANDARD",
    "49,         STANDARD",
    "50,         BULK",
    "2147483647, BULK"
  })
  void picksTierByQuantity(int quantity, Tier expected) {
    assertThat(Tier.forQuantity(quantity)).isEqualTo(expected);
  }

  @Test
  void rejectsMinusOne() {
    assertThatThrownBy(() -> Tier.forQuantity(-1))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("negative");
  }
}
