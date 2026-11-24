package com.example.billing;

import java.math.BigDecimal;

/** An invoice. */
public record Invoice(String number, String customer, BigDecimal total) {}
