package com.example.orders

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull
import kotlin.test.assertTrue

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

    @Test
    fun `page returns at most page size orders`() {
        assertEquals(10, makeStore(50).page(1, pageSize = 10).size)
    }

    @Test
    fun `page leaves out cancelled orders`() {
        assertTrue(makeStore(50, cancelledEvery = 5).page(1, pageSize = 10).none { it.status == "cancelled" })
    }

    @Test
    fun `page rejects page zero`() {
        assertFailsWith<IllegalArgumentException> { makeStore(5).page(0) }
    }
}
