package com.example.rates;

import java.math.BigDecimal;
import java.util.logging.Level;
import java.util.logging.Logger;

/** Exchange-rate client. */
public final class RateClient {
  private static final Logger LOG = Logger.getLogger(RateClient.class.getName());
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
      LOG.log(Level.WARNING, "rate lookup failed", e);
      return null;
    }
  }
}
