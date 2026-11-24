package com.example.weather;

import java.io.IOException;
import okhttp3.HttpUrl;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

/** Weather forecast client. */
public final class ForecastClient {
  private final OkHttpClient http;
  private final HttpUrl base;

  public ForecastClient(OkHttpClient http, HttpUrl base) {
    this.http = http;
    this.base = base;
  }

  HttpUrl forecastUrl(String city) {
    return base.newBuilder().addPathSegment("forecast").addPathSegment(city).build();
  }

  public String fetchForecast(String city) throws IOException {
    Request request = new Request.Builder().url(forecastUrl(city)).build();
    try (Response response = http.newCall(request).execute()) {
      if (!response.isSuccessful()) {
        throw new IOException("forecast for " + city + " failed: HTTP " + response.code());
      }
      return response.body().string();
    }
  }
}
