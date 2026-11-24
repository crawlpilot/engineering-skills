package com.example.accounts;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;

/** Applies the schema migrations in db/migration, in order. Production runs this on deploy. */
public final class Migrations {
  static final List<String> FILES = List.of("V1__create_users.sql");

  private Migrations() {}

  public static void apply(Connection conn) throws SQLException {
    for (String file : FILES) {
      try (Statement st = conn.createStatement()) {
        st.execute(read("/db/migration/" + file));
      }
    }
  }

  private static String read(String resource) {
    try (InputStream in = Migrations.class.getResourceAsStream(resource)) {
      if (in == null) {
        throw new IllegalStateException("missing migration " + resource);
      }
      return new String(in.readAllBytes(), StandardCharsets.UTF_8);
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    }
  }
}
