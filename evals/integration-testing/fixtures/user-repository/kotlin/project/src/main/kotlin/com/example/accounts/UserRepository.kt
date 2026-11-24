package com.example.accounts

import java.sql.Connection
import java.sql.SQLException

/** A stored user. Emails are lower-cased. */
data class User(val id: Long, val email: String, val name: String)

/** A user with this email already exists. */
class DuplicateEmailException(email: String, cause: Throwable) :
    RuntimeException("a user with email $email already exists", cause)

/**
 * User storage in PostgreSQL.
 *
 * Emails are stored lower-cased and are unique, so lookups ignore case.
 */
class UserRepository(private val conn: Connection) {

    /** Inserts a user. Throws [DuplicateEmailException] if the email is taken, in any case. */
    fun save(email: String, name: String): User {
        val normalized = email.lowercase()
        try {
            conn.prepareStatement("INSERT INTO users (email, name) VALUES (?, ?) RETURNING id").use { ps ->
                ps.setString(1, normalized)
                ps.setString(2, name)
                ps.executeQuery().use { rs ->
                    rs.next()
                    return User(rs.getLong(1), normalized, name)
                }
            }
        } catch (e: SQLException) {
            if (e.sqlState == UNIQUE_VIOLATION) throw DuplicateEmailException(normalized, e)
            throw IllegalStateException("could not save user $normalized", e)
        }
    }

    /** Returns the user with this email, ignoring case, or null. */
    fun findByEmail(email: String): User? =
        conn.prepareStatement("SELECT id, email, name FROM users WHERE email = ?").use { ps ->
            ps.setString(1, email.lowercase())
            ps.executeQuery().use { rs ->
                if (rs.next()) User(rs.getLong("id"), rs.getString("email"), rs.getString("name")) else null
            }
        }

    private companion object {
        const val UNIQUE_VIOLATION = "23505"
    }
}
