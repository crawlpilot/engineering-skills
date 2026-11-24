package com.example.accounts

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.BeforeEach
import org.testcontainers.junit.jupiter.Container
import org.testcontainers.junit.jupiter.Testcontainers
import org.testcontainers.postgresql.PostgreSQLContainer
import java.sql.Connection
import java.sql.DriverManager
import java.util.UUID
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull

/** UserRepository against real PostgreSQL, schema built by the project's migrations. */
@Testcontainers
class UserRepositoryIT {

    companion object {
        @Container
        @JvmStatic
        val postgres = PostgreSQLContainer("postgres:17-alpine")

        fun connect(): Connection = DriverManager.getConnection(postgres.jdbcUrl, postgres.username, postgres.password)

        @BeforeAll
        @JvmStatic
        fun migrate() {
            connect().use { Migrations.apply(it) }
        }

        // Unique per test, so tests never see each other's rows.
        fun uniqueEmail(prefix: String) = "$prefix-${UUID.randomUUID().toString().take(8)}@example.com"
    }

    private lateinit var conn: Connection
    private lateinit var repo: UserRepository

    @BeforeEach
    fun open() {
        conn = connect()
        repo = UserRepository(conn)
    }

    @AfterEach
    fun close() {
        conn.close()
    }

    @Test
    fun `saves and finds a user`() {
        val email = uniqueEmail("user")
        val saved = repo.save(email, "Ada")
        assertEquals(saved, repo.findByEmail(email))
    }

    @Test
    fun `finds the right user among several`() {
        repo.save(uniqueEmail("first"), "First")
        val second = uniqueEmail("second")
        val saved = repo.save(second, "Second")
        assertEquals(saved, repo.findByEmail(second))
    }

    @Test
    fun `lookup ignores case`() {
        val email = uniqueEmail("user")
        val saved = repo.save(email, "Ada")
        assertEquals(saved, repo.findByEmail(email.uppercase()))
    }

    @Test
    fun `returns null when not found`() {
        assertNull(repo.findByEmail(uniqueEmail("missing")))
    }

    @Test
    fun `rejects a duplicate email in any case`() {
        val email = uniqueEmail("user")
        repo.save(email, "Ada")
        assertFailsWith<DuplicateEmailException> { repo.save(email.uppercase(), "Imposter") }
    }
}
