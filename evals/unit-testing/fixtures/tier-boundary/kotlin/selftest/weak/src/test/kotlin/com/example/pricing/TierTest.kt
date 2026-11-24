package com.example.pricing

import kotlin.test.Test
import kotlin.test.assertEquals

// Deliberately weak suite used only by the fixture self-test.
class TierTest {

    @Test
    fun `typical order is standard`() {
        assertEquals(Tier.STANDARD, Tier.forQuantity(10))
    }

    @Test
    fun `large order is bulk`() {
        assertEquals(Tier.BULK, Tier.forQuantity(100))
    }
}
