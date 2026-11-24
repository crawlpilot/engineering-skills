package com.example.rates;

import java.math.BigDecimal;
import java.math.RoundingMode;

/** Currency conversion. */
public final class Converter {
  private final RateClient rates;

  public Converter(RateClient rates) {
    this.rates = rates;
  }

  /** Converts a USD amount to a currency, rounded to cents. */
  public BigDecimal convert(BigDecimal amountUsd, String currency) {
    return amountUsd.multiply(rates.fetchRate(currency)).setScale(2, RoundingMode.HALF_EVEN);
  }
}
