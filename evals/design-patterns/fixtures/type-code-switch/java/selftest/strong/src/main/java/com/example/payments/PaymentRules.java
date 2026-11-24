package com.example.payments;

import java.math.BigDecimal;

/** Per-method business rules. Kept for existing callers; the rules live on {@link PaymentMethod}. */
public final class PaymentRules {
  private PaymentRules() {}

  public static BigDecimal feePercent(PaymentMethod method) {
    return method.feePercent();
  }

  public static int settlementDays(PaymentMethod method) {
    return method.settlementDays();
  }

  public static boolean refundable(PaymentMethod method) {
    return method.refundable();
  }
}
