package com.example.orders;

/** An order. Status is "open", "shipped" or "cancelled". */
public record Order(int id, String customer, String status) {}
