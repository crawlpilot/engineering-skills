package com.example.rates

import java.io.IOException
import java.time.LocalDate
import java.time.format.DateTimeParseException
import java.util.logging.Logger

/** Bank holiday client. */
class HolidayClient(private val transport: Transport) {

    /** Returns this year's bank holidays in a country, from a comma-separated list of ISO dates. */
    fun holidays(country: String): List<LocalDate> {
        val body = try {
            transport.get("/holidays/$country")
        } catch (e: IOException) {
            log.warning("holiday lookup failed for $country")
            throw ServiceException("could not fetch holidays for $country", e)
        }
        return try {
            body.trim().split(",").map { LocalDate.parse(it.trim()) }
        } catch (e: DateTimeParseException) {
            throw ServiceException("malformed holiday list for $country", e)
        }
    }

    private companion object {
        val log: Logger = Logger.getLogger(HolidayClient::class.java.name)
    }
}
