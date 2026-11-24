package com.example.payments

import java.math.BigDecimal

/**
 * Per-method business rules.
 *
 * Each `when` lists every method and has no `else`, so adding a method that isn't
 * given a fee, settlement time and refund policy doesn't compile.
 */
object PaymentRules {

    /** Processing fee, as a percentage of the amount. */
    fun feePercent(method: PaymentMethod): BigDecimal = when (method) {
        PaymentMethod.CARD -> BigDecimal("2.9")
        PaymentMethod.BANK_TRANSFER -> BigDecimal("0.8")
        PaymentMethod.WALLET -> BigDecimal("1.5")
        PaymentMethod.VOUCHER -> BigDecimal.ZERO
    }

    /** Working days until the money reaches the merchant. */
    fun settlementDays(method: PaymentMethod): Int = when (method) {
        PaymentMethod.CARD -> 2
        PaymentMethod.BANK_TRANSFER -> 3
        PaymentMethod.WALLET -> 1
        PaymentMethod.VOUCHER -> 0
    }

    /** Whether a payment by this method can be refunded to the same method. */
    fun refundable(method: PaymentMethod): Boolean = when (method) {
        PaymentMethod.CARD, PaymentMethod.BANK_TRANSFER -> true
        PaymentMethod.WALLET, PaymentMethod.VOUCHER -> false
    }
}
