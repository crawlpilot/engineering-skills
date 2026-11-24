package com.example.billing

import java.math.BigDecimal

/** Creates invoices. */
object InvoiceFactory {
    fun create(number: String, customer: String, total: BigDecimal) = Invoice(number, customer, total)
}

/** Builds invoices. */
class InvoiceBuilder {
    var number: String = ""
    var customer: String = ""
    var total: BigDecimal = BigDecimal.ZERO

    fun build() = InvoiceFactory.create(number, customer, total)
}
