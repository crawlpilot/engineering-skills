package com.example.pricing

import java.math.BigDecimal
import kotlin.test.Test
import kotlin.test.assertEquals

class MoneyTest {

    @Test
    fun `rounds to two decimal places`() {
        assertEquals(BigDecimal("10.00"), Money.of("10.005").amount)
    }

    @Test
    fun `adds amounts`() {
        assertEquals(Money.of("3.35"), Money.of("1.10") + Money.of("2.25"))
    }
}
