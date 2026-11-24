package com.example.billing;

import java.math.BigDecimal;

/** Builds invoices. */
public final class InvoiceBuilder {
  private String number = "";
  private String customer = "";
  private BigDecimal total = BigDecimal.ZERO;

  public InvoiceBuilder number(String value) {
    this.number = value;
    return this;
  }

  public InvoiceBuilder customer(String value) {
    this.customer = value;
    return this;
  }

  public InvoiceBuilder total(BigDecimal value) {
    this.total = value;
    return this;
  }

  public Invoice build() {
    return new Invoice(number, customer, total);
  }
}
