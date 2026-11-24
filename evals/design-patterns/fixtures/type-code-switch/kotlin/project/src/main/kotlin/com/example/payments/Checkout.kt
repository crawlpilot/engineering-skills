package com.example.payments

import java.math.BigDecimal
import java.math.RoundingMode

/** What the checkout page shows for a payment. */
data class Quote(val fee: BigDecimal, val settlementDays: Int, val refundable: Boolean)

/** Prices a payment for the checkout page. */
class Checkout {
    fun quote(method: PaymentMethod, amount: BigDecimal): Quote {
        val fee = (amount * PaymentRules.feePercent(method)).divide(BigDecimal("100"), 2, RoundingMode.HALF_EVEN)
        return Quote(fee, PaymentRules.settlementDays(method), PaymentRules.refundable(method))
    }
}
