package com.example.accounts

import java.sql.Connection

/** Applies the schema migrations in db/migration, in order. Production runs this on deploy. */
object Migrations {
    internal val files = listOf("V1__create_users.sql")

    fun apply(conn: Connection) {
        for (file in files) {
            val sql = Migrations::class.java.getResource("/db/migration/$file")?.readText()
                ?: error("missing migration $file")
            conn.createStatement().use { it.execute(sql) }
        }
    }
}
