package com.example.accounts;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class UserRepositoryTest {
  @Test
  void createsARepository() {
    assertThat(new UserRepository(null)).isNotNull();
  }
}
