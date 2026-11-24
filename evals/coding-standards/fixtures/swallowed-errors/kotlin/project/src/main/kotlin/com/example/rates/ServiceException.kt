package com.example.rates

/** A call to an upstream service failed. The message names what was being fetched. */
class ServiceException(message: String, cause: Throwable) : RuntimeException(message, cause)
