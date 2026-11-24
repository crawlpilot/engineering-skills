package com.example.payments

// Hidden grading test: behaviour of every method is unchanged.
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import java.math.BigDecimal
import kotlin.test.assertEquals

class HiddenCheckoutTest {

    @ParameterizedTest
    @CsvSource(
        "CARD,          7.25, 2, true",
        "BANK_TRANSFER, 2.00, 3, true",
        "WALLET,        3.75, 1, false",
        "VOUCHER,       0.00, 0, false",
    )
    fun `quotes each method`(method: PaymentMethod, fee: String, days: Int, refundable: Boolean) {
        assertEquals(Quote(BigDecimal(fee), days, refundable), Checkout().quote(method, BigDecimal("250")))
    }
}
