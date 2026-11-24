package com.example.rates;

import static org.assertj.core.api.Assertions.assertThat;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class RateClientTest {

  @Test
  void parsesRate() throws Exception {
    assertThat(new RateClient(path -> "0.92\n").fetchRate("EUR")).isEqualByComparingTo("0.92");
  }

  @Test
  void convertsAmount() throws Exception {
    Converter converter = new Converter(new RateClient(path -> "0.92"));
    assertThat(converter.convert(new BigDecimal("10"), "EUR")).isEqualByComparingTo("9.20");
  }
}
