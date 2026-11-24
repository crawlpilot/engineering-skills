package com.example.accounts;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Locale;
import java.util.Optional;

/**
 * User storage in PostgreSQL.
 *
 * <p>Emails are stored lower-cased and are unique, so lookups ignore case.
 */
public final class UserRepository {
  private static final String UNIQUE_VIOLATION = "23505";
  private final Connection conn;

  public UserRepository(Connection conn) {
    this.conn = conn;
  }

  /** Inserts a user. Throws DuplicateEmailException if the email is taken, in any case. */
  public User save(String email, String name) {
    String normalized = email.toLowerCase(Locale.ROOT);
    try (PreparedStatement ps =
        conn.prepareStatement("INSERT INTO users (email, name) VALUES (?, ?) RETURNING id")) {
      ps.setString(1, normalized);
      ps.setString(2, name);
      try (ResultSet rs = ps.executeQuery()) {
        rs.next();
        return new User(rs.getLong(1), normalized, name);
      }
    } catch (SQLException e) {
      if (UNIQUE_VIOLATION.equals(e.getSQLState())) {
        throw new DuplicateEmailException(normalized, e);
      }
      throw new IllegalStateException("could not save user " + normalized, e);
    }
  }

  /** Returns the user with this email, ignoring case. */
  public Optional<User> findByEmail(String email) {
    try (PreparedStatement ps =
        conn.prepareStatement("SELECT id, email, name FROM users WHERE email = ?")) {
      ps.setString(1, email.toLowerCase(Locale.ROOT));
      try (ResultSet rs = ps.executeQuery()) {
        if (!rs.next()) {
          return Optional.empty();
        }
        return Optional.of(new User(rs.getLong("id"), rs.getString("email"), rs.getString("name")));
      }
    } catch (SQLException e) {
      throw new IllegalStateException("could not look up user " + email, e);
    }
  }
}
