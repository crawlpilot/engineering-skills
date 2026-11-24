package com.example.billing;

import static org.assertj.core.api.Assertions.assertThat;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class InvoiceServiceTest {
  @Test
  void numbersInvoicesFromTheSequence() {
    assertThat(new InvoiceService().create("acme", new BigDecimal("12.50"), 42))
        .isEqualTo(new Invoice("INV-00042", "acme", new BigDecimal("12.50")));
  }
}
