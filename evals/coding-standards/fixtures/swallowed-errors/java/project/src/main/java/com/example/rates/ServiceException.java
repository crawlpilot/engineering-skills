package com.example.rates;

/** A call to an upstream service failed. The message names what was being fetched. */
public class ServiceException extends RuntimeException {
  public ServiceException(String message, Throwable cause) {
    super(message, cause);
  }
}
