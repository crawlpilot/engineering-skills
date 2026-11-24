package com.example.rates;

import java.math.BigDecimal;

/** Exchange-rate client. */
public final class RateClient {
  private final Transport transport;

  public RateClient(Transport transport) {
    this.transport = transport;
  }

  /** Returns the rate from USD to a currency, for example 0.92 for EUR. */
  public BigDecimal fetchRate(String currency) {
    try {
      String body = transport.get("/rates/" + currency);
      return new BigDecimal(body.trim());
    } catch (Exception e) {
      return null;
    }
  }
}
