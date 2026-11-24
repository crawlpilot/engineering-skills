package com.example.rates

import java.io.IOException

/** The HTTP seam the clients call through. */
fun interface Transport {
    /** Returns the response body. */
    @Throws(IOException::class)
    fun get(path: String): String
}
