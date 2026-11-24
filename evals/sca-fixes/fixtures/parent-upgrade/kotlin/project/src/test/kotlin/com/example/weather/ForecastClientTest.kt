package com.example.weather

import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.OkHttpClient
import kotlin.test.Test
import kotlin.test.assertEquals

class ForecastClientTest {
    @Test
    fun `encodes the city in the path`() {
        val client = ForecastClient(OkHttpClient(), "https://api.example.com/".toHttpUrl())
        assertEquals("https://api.example.com/forecast/S%C3%A3o%20Paulo", client.forecastUrl("São Paulo").toString())
    }
}
