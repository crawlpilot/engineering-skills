package com.example.payments;

import java.math.BigDecimal;

/**
 * How a customer pays, with the rules for each method.
 *
 * <p>Every constant must state all of its rules, so adding a method without deciding its fee,
 * settlement time and refund policy does not compile.
 */
public enum PaymentMethod {
  CARD("2.9", 2, true),
  BANK_TRANSFER("0.8", 3, true),
  WALLET("1.5", 1, false),
  VOUCHER("0", 0, false);

  private final BigDecimal feePercent;
  private final int settlementDays;
  private final boolean refundable;

  PaymentMethod(String feePercent, int settlementDays, boolean refundable) {
    this.feePercent = new BigDecimal(feePercent);
    this.settlementDays = settlementDays;
    this.refundable = refundable;
  }

  /** Processing fee, as a percentage of the amount. */
  public BigDecimal feePercent() {
    return feePercent;
  }

  /** Working days until the money reaches the merchant. */
  public int settlementDays() {
    return settlementDays;
  }

  /** Whether a payment by this method can be refunded to the same method. */
  public boolean refundable() {
    return refundable;
  }
}
