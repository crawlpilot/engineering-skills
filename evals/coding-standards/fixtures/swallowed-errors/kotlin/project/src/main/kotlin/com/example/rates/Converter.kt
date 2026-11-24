package com.example.rates

import java.math.BigDecimal
import java.math.RoundingMode

/** Currency conversion. */
class Converter(private val rates: RateClient) {

    /** Converts a USD amount to a currency, rounded to cents. */
    fun convert(amountUsd: BigDecimal, currency: String): BigDecimal =
        (amountUsd * rates.fetchRate(currency)!!).setScale(2, RoundingMode.HALF_EVEN)
}
