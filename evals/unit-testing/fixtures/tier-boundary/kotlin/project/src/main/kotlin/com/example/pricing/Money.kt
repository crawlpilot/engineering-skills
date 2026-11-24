package com.example.pricing

import java.math.BigDecimal
import java.math.RoundingMode

/** An amount of money in a single currency, held to two decimal places. */
data class Money private constructor(val amount: BigDecimal) {

    operator fun plus(other: Money): Money = of(amount + other.amount)

    companion object {
        fun of(amount: BigDecimal): Money = Money(amount.setScale(2, RoundingMode.HALF_EVEN))

        fun of(amount: String): Money = of(BigDecimal(amount))
    }
}
