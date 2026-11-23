package com.example.pricing

import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

// Known-good suite used only by the fixture self-test.
class TierTest {

    @ParameterizedTest
    @CsvSource(
        "0,          FREE",
        "1,          STANDARD",
        "49,         STANDARD",
        "50,         BULK",
        "2147483647, BULK",
    )
    fun `picks tier by quantity`(quantity: Int, expected: Tier) {
        assertEquals(expected, Tier.forQuantity(quantity))
    }

    @Test
    fun `rejects minus one`() {
        val error = assertFailsWith<IllegalArgumentException> { Tier.forQuantity(-1) }
        assertEquals("quantity must not be negative: -1", error.message)
    }
}
