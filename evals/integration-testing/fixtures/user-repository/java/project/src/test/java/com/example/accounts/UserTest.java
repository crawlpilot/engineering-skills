package com.example.accounts;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class UserTest {
  @Test
  void usersCompareByValue() {
    assertThat(new User(1, "a@example.com", "A")).isEqualTo(new User(1, "a@example.com", "A"));
  }
}
