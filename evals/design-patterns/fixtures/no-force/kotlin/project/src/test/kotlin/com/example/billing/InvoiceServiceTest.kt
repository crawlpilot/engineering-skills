package com.example.billing

import java.math.BigDecimal
import kotlin.test.Test
import kotlin.test.assertEquals

class InvoiceServiceTest {
    @Test
    fun `numbers invoices from the sequence`() {
        assertEquals(
            Invoice("INV-00042", "acme", BigDecimal("12.50")),
            InvoiceService().create("acme", BigDecimal("12.50"), 42),
        )
    }
}
