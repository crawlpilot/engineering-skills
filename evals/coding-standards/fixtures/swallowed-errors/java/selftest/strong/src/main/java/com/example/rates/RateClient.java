package com.example.rates;

import java.io.IOException;
import java.math.BigDecimal;
import java.util.logging.Logger;

/** Exchange-rate client. */
public final class RateClient {
  private static final Logger LOG = Logger.getLogger(RateClient.class.getName());
  private final Transport transport;

  public RateClient(Transport transport) {
    this.transport = transport;
  }

  /**
   * Returns the rate from USD to a currency, for example 0.92 for EUR.
   *
   * @throws ServiceException if the rate service can't be reached or returns a malformed rate
   */
  public BigDecimal fetchRate(String currency) {
    String body;
    try {
      body = transport.get("/rates/" + currency);
    } catch (IOException e) {
      LOG.warning("rate lookup failed for " + currency);
      throw new ServiceException("could not fetch the " + currency + " rate", e);
    }
    try {
      return new BigDecimal(body.trim());
    } catch (NumberFormatException e) {
      throw new ServiceException("malformed " + currency + " rate", e);
    }
  }
}
