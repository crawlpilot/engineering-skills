package com.example.orders;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class OrderStoreTest {

  static OrderStore makeStore(int count, int cancelledEvery) {
    OrderStore store = new OrderStore();
    for (int i = 1; i <= count; i++) {
      String status = cancelledEvery > 0 && i % cancelledEvery == 0 ? "cancelled" : "open";
      store.add(new Order(i, "c" + i, status));
    }
    return store;
  }

  @Test
  void getReturnsOrderById() {
    assertThat(makeStore(3, 0).get(2)).contains(new Order(2, "c2", "open"));
  }

  @Test
  void getReturnsEmptyWhenMissing() {
    assertThat(makeStore(3, 0).get(99)).isEmpty();
  }

  @Test
  void allKeepsInsertionOrder() {
    assertThat(makeStore(3, 0).all()).extracting(Order::id).containsExactly(1, 2, 3);
  }
}
