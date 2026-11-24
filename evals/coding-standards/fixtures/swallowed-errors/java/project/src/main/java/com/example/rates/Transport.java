package com.example.rates;

import java.io.IOException;

/** The HTTP seam the clients call through. */
public interface Transport {
  /** Returns the response body. */
  String get(String path) throws IOException;
}
