package com.example.weather;

import static org.assertj.core.api.Assertions.assertThat;

import okhttp3.HttpUrl;
import okhttp3.OkHttpClient;
import org.junit.jupiter.api.Test;

class ForecastClientTest {
  @Test
  void encodesTheCityInThePath() {
    ForecastClient client =
        new ForecastClient(new OkHttpClient(), HttpUrl.get("https://api.example.com/"));
    assertThat(client.forecastUrl("São Paulo").toString())
        .isEqualTo("https://api.example.com/forecast/S%C3%A3o%20Paulo");
  }
}
