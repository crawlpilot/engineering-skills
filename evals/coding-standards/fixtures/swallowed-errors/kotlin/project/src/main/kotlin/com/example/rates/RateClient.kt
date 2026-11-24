package com.example.rates

import java.math.BigDecimal

/** Exchange-rate client. */
class RateClient(private val transport: Transport) {

    /** Returns the rate from USD to a currency, for example 0.92 for EUR. */
    fun fetchRate(currency: String): BigDecimal? =
        try {
            BigDecimal(transport.get("/rates/$currency").trim())
        } catch (e: Exception) {
            null
        }
}
