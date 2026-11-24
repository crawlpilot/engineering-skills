package com.example.payments

import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import java.math.BigDecimal
import kotlin.test.assertEquals

class CheckoutTest {

    @ParameterizedTest
    @CsvSource(
        "CARD,          2.90, 2, true",
        "BANK_TRANSFER, 0.80, 3, true",
        "WALLET,        1.50, 1, false",
        "VOUCHER,       0.00, 0, false",
    )
    fun `quotes each method`(method: PaymentMethod, fee: String, days: Int, refundable: Boolean) {
        assertEquals(Quote(BigDecimal(fee), days, refundable), Checkout().quote(method, BigDecimal("100")))
    }
}
