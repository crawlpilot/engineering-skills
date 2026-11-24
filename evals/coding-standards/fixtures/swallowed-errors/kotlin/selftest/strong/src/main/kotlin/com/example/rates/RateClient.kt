package com.example.rates

import java.io.IOException
import java.math.BigDecimal
import java.util.logging.Logger

/** Exchange-rate client. */
class RateClient(private val transport: Transport) {

    /**
     * Returns the rate from USD to a currency, for example 0.92 for EUR.
     *
     * @throws ServiceException if the rate service can't be reached or returns a malformed rate
     */
    fun fetchRate(currency: String): BigDecimal {
        val body = try {
            transport.get("/rates/$currency")
        } catch (e: IOException) {
            log.warning("rate lookup failed for $currency")
            throw ServiceException("could not fetch the $currency rate", e)
        }
        return try {
            BigDecimal(body.trim())
        } catch (e: NumberFormatException) {
            throw ServiceException("malformed $currency rate", e)
        }
    }

    private companion object {
        val log: Logger = Logger.getLogger(RateClient::class.java.name)
    }
}
