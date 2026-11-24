package com.example.rates

import java.math.BigDecimal
import java.util.logging.Level
import java.util.logging.Logger

/** Exchange-rate client. */
class RateClient(private val transport: Transport) {

    /** Returns the rate from USD to a currency, for example 0.92 for EUR. */
    fun fetchRate(currency: String): BigDecimal? =
        try {
            BigDecimal(transport.get("/rates/$currency").trim())
        } catch (e: Exception) {
            log.log(Level.WARNING, "rate lookup failed", e)
            null
        }

    private companion object {
        val log: Logger = Logger.getLogger(RateClient::class.java.name)
    }
}
