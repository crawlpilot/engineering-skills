package com.example.rates;

import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.Arrays;
import java.util.List;
import java.util.logging.Logger;

/** Bank holiday client. */
public final class HolidayClient {
  private static final Logger LOG = Logger.getLogger(HolidayClient.class.getName());
  private final Transport transport;

  public HolidayClient(Transport transport) {
    this.transport = transport;
  }

  /** Returns this year's bank holidays in a country, from a comma-separated list of ISO dates. */
  public List<LocalDate> holidays(String country) {
    String body;
    try {
      body = transport.get("/holidays/" + country);
    } catch (IOException e) {
      LOG.warning("holiday lookup failed for " + country);
      throw new ServiceException("could not fetch holidays for " + country, e);
    }
    try {
      return Arrays.stream(body.trim().split(",")).map(String::trim).map(LocalDate::parse).toList();
    } catch (DateTimeParseException e) {
      throw new ServiceException("malformed holiday list for " + country, e);
    }
  }
}
