package com.example.pricing

/** Price tier for an order, chosen by the number of items in it. */
enum class Tier {
    FREE,
    STANDARD,
    BULK,
    ;

    companion object {
        /** Orders of this many items or more are priced as bulk. */
        const val BULK_THRESHOLD = 50

        /**
         * Returns the tier for an order quantity.
         *
         * - 0 items: [FREE]
         * - 1 to 49 items: [STANDARD]
         * - 50 items or more: [BULK]
         *
         * @throws IllegalArgumentException if [quantity] is negative
         */
        fun forQuantity(quantity: Int): Tier {
            require(quantity >= 0) { "quantity must not be negative: $quantity" }
            if (quantity == 0) return FREE
            if (quantity > BULK_THRESHOLD) return BULK
            return STANDARD
        }
    }
}
