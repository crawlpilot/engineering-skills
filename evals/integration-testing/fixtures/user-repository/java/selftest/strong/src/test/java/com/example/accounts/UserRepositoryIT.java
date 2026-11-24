package com.example.accounts;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.sql.Connection;
import java.sql.DriverManager;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.postgresql.PostgreSQLContainer;

/** UserRepository against real PostgreSQL, schema built by the project's migrations. */
@Testcontainers
class UserRepositoryIT {

  @Container static final PostgreSQLContainer POSTGRES = new PostgreSQLContainer("postgres:17-alpine");

  private Connection conn;
  private UserRepository repo;

  @BeforeAll
  static void migrate() throws Exception {
    try (Connection c = connect()) {
      Migrations.apply(c);
    }
  }

  static Connection connect() throws Exception {
    return DriverManager.getConnection(POSTGRES.getJdbcUrl(), POSTGRES.getUsername(), POSTGRES.getPassword());
  }

  @BeforeEach
  void open() throws Exception {
    conn = connect();
    repo = new UserRepository(conn);
  }

  @AfterEach
  void close() throws Exception {
    conn.close();
  }

  // Unique per test, so tests never see each other's rows.
  static String uniqueEmail(String prefix) {
    return prefix + "-" + UUID.randomUUID().toString().substring(0, 8) + "@example.com";
  }

  @Test
  void savesAndFindsAUser() {
    String email = uniqueEmail("user");
    User saved = repo.save(email, "Ada");
    assertThat(repo.findByEmail(email)).contains(saved);
  }

  @Test
  void findsTheRightUserAmongSeveral() {
    repo.save(uniqueEmail("first"), "First");
    String second = uniqueEmail("second");
    User saved = repo.save(second, "Second");
    assertThat(repo.findByEmail(second)).contains(saved);
  }

  @Test
  void lookupIgnoresCase() {
    String email = uniqueEmail("user");
    User saved = repo.save(email, "Ada");
    assertThat(repo.findByEmail(email.toUpperCase())).contains(saved);
  }

  @Test
  void returnsEmptyWhenNotFound() {
    assertThat(repo.findByEmail(uniqueEmail("missing"))).isEmpty();
  }

  @Test
  void rejectsADuplicateEmailInAnyCase() {
    String email = uniqueEmail("user");
    repo.save(email, "Ada");
    assertThatThrownBy(() -> repo.save(email.toUpperCase(), "Imposter"))
        .isInstanceOf(DuplicateEmailException.class);
  }
}
