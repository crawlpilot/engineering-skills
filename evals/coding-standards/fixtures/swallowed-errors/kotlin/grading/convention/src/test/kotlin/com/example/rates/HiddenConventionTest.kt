package com.example.rates

// Hidden grading test: the project's own error type is used, as HolidayClient does.
import java.io.IOException
import kotlin.test.Test
import kotlin.test.assertFailsWith

class HiddenConventionTest {

    @Test
    fun `uses the project error type`() {
        assertFailsWith<ServiceException> { RateClient { throw IOException("refused") }.fetchRate("EUR") }
    }
}
