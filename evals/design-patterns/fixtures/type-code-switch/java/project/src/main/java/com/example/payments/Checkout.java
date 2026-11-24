package com.example.payments;

import java.math.BigDecimal;
import java.math.RoundingMode;

/** Prices a payment for the checkout page. */
public final class Checkout {

  /** What the checkout page shows for a payment. */
  public record Quote(BigDecimal fee, int settlementDays, boolean refundable) {}

  public Quote quote(PaymentMethod method, BigDecimal amount) {
    BigDecimal fee =
        amount
            .multiply(PaymentRules.feePercent(method))
            .divide(new BigDecimal("100"), 2, RoundingMode.HALF_EVEN);
    return new Quote(fee, PaymentRules.settlementDays(method), PaymentRules.refundable(method));
  }
}
