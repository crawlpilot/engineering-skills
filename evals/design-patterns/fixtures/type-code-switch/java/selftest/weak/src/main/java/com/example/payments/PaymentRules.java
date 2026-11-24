package com.example.payments;

import java.math.BigDecimal;

/** Per-method business rules. */
public final class PaymentRules {
  private PaymentRules() {}

  /** Processing fee, as a percentage of the amount. */
  public static BigDecimal feePercent(PaymentMethod method) {
    return switch (method) {
      case CARD -> new BigDecimal("2.9");
      case BANK_TRANSFER -> new BigDecimal("0.8");
      case WALLET -> new BigDecimal("1.5");
      default -> BigDecimal.ZERO;
    };
  }

  /** Working days until the money reaches the merchant. */
  public static int settlementDays(PaymentMethod method) {
    return switch (method) {
      case CARD -> 2;
      case BANK_TRANSFER -> 3;
      case WALLET -> 1;
      default -> 0;
    };
  }

  /** Whether a payment by this method can be refunded to the same method. */
  public static boolean refundable(PaymentMethod method) {
    return switch (method) {
      case CARD, BANK_TRANSFER -> true;
      default -> false;
    };
  }
}
