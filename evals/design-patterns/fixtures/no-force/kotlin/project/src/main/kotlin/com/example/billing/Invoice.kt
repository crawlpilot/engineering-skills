package com.example.billing

import java.math.BigDecimal

/** An invoice. */
data class Invoice(val number: String, val customer: String, val total: BigDecimal)

/** Creates invoices. This is the only place an Invoice is constructed. */
class InvoiceService {
    fun create(customer: String, total: BigDecimal, sequence: Int): Invoice =
        Invoice("INV-%05d".format(sequence), customer, total)
}
