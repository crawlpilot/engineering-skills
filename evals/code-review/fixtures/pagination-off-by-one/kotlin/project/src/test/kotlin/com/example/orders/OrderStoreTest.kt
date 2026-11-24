package com.example.orders

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class OrderStoreTest {

    private fun makeStore(count: Int, cancelledEvery: Int = 0) = OrderStore().apply {
        for (i in 1..count) {
            val status = if (cancelledEvery > 0 && i % cancelledEvery == 0) "cancelled" else "open"
            add(Order(i, "c$i", status))
        }
    }

    @Test
    fun `get returns order by id`() {
        assertEquals(Order(2, "c2", "open"), makeStore(3).get(2))
    }

    @Test
    fun `get returns null when missing`() {
        assertNull(makeStore(3).get(99))
    }

    @Test
    fun `all keeps insertion order`() {
        assertEquals(listOf(1, 2, 3), makeStore(3).all().map { it.id })
    }
}
