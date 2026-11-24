package com.example.payments;

import java.math.BigDecimal;

/** Per-method business rules. WALLET was added last quarter; see feePercent and settlementDays. */
public final class PaymentRules {
  private PaymentRules() {}

  /** Processing fee, as a percentage of the amount. */
  public static BigDecimal feePercent(PaymentMethod method) {
    switch (method) {
      case CARD:
        return new BigDecimal("2.9");
      case BANK_TRANSFER:
        return new BigDecimal("0.8");
      case WALLET:
        return new BigDecimal("1.5");
      default:
        return BigDecimal.ZERO;
    }
  }

  /** Working days until the money reaches the merchant. */
  public static int settlementDays(PaymentMethod method) {
    switch (method) {
      case CARD:
        return 2;
      case BANK_TRANSFER:
        return 3;
      case WALLET:
        return 1;
      default:
        return 0;
    }
  }

  /** Whether a payment by this method can be refunded to the same method. */
  public static boolean refundable(PaymentMethod method) {
    switch (method) {
      case CARD:
        return true;
      case BANK_TRANSFER:
        return true;
      default:
        return false;
    }
  }
}
