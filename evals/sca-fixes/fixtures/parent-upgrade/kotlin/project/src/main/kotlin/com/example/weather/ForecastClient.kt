package com.example.weather

import okhttp3.HttpUrl
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.IOException

/** Weather forecast client. */
class ForecastClient(private val http: OkHttpClient, private val base: HttpUrl) {

    internal fun forecastUrl(city: String): HttpUrl =
        base.newBuilder().addPathSegment("forecast").addPathSegment(city).build()

    fun fetchForecast(city: String): String {
        val request = Request.Builder().url(forecastUrl(city)).build()
        http.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("forecast for $city failed: HTTP ${response.code}")
            return response.body!!.string()
        }
    }
}
