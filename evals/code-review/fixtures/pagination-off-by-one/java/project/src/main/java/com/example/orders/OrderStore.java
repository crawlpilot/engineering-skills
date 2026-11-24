package com.example.orders;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

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
}
