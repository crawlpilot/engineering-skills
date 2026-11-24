package com.example.billing;

import java.math.BigDecimal;

/** Creates invoices. This is the only place an Invoice is constructed. */
public final class InvoiceService {
  public Invoice create(String customer, BigDecimal total, int sequence) {
    return new Invoice("INV-%05d".formatted(sequence), customer, total);
  }
}
