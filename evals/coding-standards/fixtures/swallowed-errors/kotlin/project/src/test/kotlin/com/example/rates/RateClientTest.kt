package com.example.rates

import java.math.BigDecimal
import kotlin.test.Test
import kotlin.test.assertEquals

class RateClientTest {

    @Test
    fun `parses rate`() {
        assertEquals(BigDecimal("0.92"), RateClient { "0.92\n" }.fetchRate("EUR"))
    }

    @Test
    fun `converts amount`() {
        assertEquals(BigDecimal("9.20"), Converter(RateClient { "0.92" }).convert(BigDecimal("10"), "EUR"))
    }
}
