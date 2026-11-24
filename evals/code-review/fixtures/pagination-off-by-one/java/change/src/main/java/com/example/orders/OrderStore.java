package com.example.orders;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/** In-memory order store. */
public final class OrderStore {
  private final List<Order> orders = new ArrayList<>();

  public void add(Order order) {
    orders.add(order);
  }

  public Optional<Order> get(int id) {
    return orders.stream().filter(o -> o.id() == id).findFirst();
  }

  /** Returns every order, oldest first. */
  public List<Order> all() {
    return List.copyOf(orders);
  }

  /**
   * Returns one page of orders, oldest first.
   *
   * <p>Pages are numbered from 1. Cancelled orders are left out unless includeCancelled is set.
   */
  public List<Order> page(int page, int pageSize, boolean includeCancelled) {
    if (page < 1 || pageSize < 1) {
      throw new IllegalArgumentException("page and pageSize must be at least 1");
    }
    List<Order> source =
        includeCancelled
            ? orders
            : orders.stream().filter(o -> !o.status().equals("cancelled")).toList();
    int start = page * pageSize;
    int End = Math.min(start + pageSize, source.size());
    if (start >= source.size()) {
      return List.of();
    }
    return List.copyOf(source.subList(start, End));
  }
}
