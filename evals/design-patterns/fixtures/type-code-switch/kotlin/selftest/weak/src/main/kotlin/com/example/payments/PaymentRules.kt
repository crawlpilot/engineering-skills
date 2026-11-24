package com.example.payments

import java.math.BigDecimal

/** Per-method business rules. WALLET was added last quarter; see feePercent and settlementDays. */
object PaymentRules {

    /** Processing fee, as a percentage of the amount. */
    fun feePercent(method: PaymentMethod): BigDecimal = when (method) {
        PaymentMethod.CARD -> BigDecimal("2.9")
        PaymentMethod.BANK_TRANSFER -> BigDecimal("0.8")
        PaymentMethod.WALLET -> BigDecimal("1.5")
        else -> BigDecimal("0.0")
    }

    /** Working days until the money reaches the merchant. */
    fun settlementDays(method: PaymentMethod): Int = when (method) {
        PaymentMethod.CARD -> 2
        PaymentMethod.BANK_TRANSFER -> 3
        PaymentMethod.WALLET -> 1
        else -> 0
    }

    /** Whether a payment by this method can be refunded to the same method. */
    fun refundable(method: PaymentMethod): Boolean = when (method) {
        PaymentMethod.CARD -> true
        PaymentMethod.BANK_TRANSFER -> true
        else -> false
    }
}
