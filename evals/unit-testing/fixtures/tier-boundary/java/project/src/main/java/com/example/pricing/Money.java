package com.example.pricing;

import java.math.BigDecimal;
import java.math.RoundingMode;

/** An amount of money in a single currency, held to two decimal places. */
public record Money(BigDecimal amount) {

  public Money {
    amount = amount.setScale(2, RoundingMode.HALF_EVEN);
  }

  public static Money of(String amount) {
    return new Money(new BigDecimal(amount));
  }

  public Money plus(Money other) {
    return new Money(amount.add(other.amount));
  }
}
