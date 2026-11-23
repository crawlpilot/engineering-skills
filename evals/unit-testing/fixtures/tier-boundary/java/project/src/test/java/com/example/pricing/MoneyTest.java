package com.example.pricing;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class MoneyTest {

  @Test
  void roundsToTwoDecimalPlaces() {
    assertThat(Money.of("10.005").amount()).isEqualByComparingTo("10.00");
  }

  @Test
  void addsAmounts() {
    assertThat(Money.of("1.10").plus(Money.of("2.25"))).isEqualTo(Money.of("3.35"));
  }
}
